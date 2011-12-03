# encoding: utf-8

from os.path import walk, isfile, isdir, join
from lxml.html import parse
from operator import attrgetter, itemgetter
from itertools import islice, izip
from countries import *
from copy import deepcopy
import csv
import json

def get_files(arg, dirname, fnames):
    todel = []
    for fname in fnames:
        if not isdir(join(dirname, fname)) and not fname.endswith('.html'):
            todel.append(fname)
    for i in todel:
        del(fnames[fnames.index(i)])

    for f in fnames:
        if isfile(join(dirname,f)):
            arg+= [(dirname, f)]

def extract_results():
    """ Extracts listings from the downloaded pages

    Returns: [ ( category, [{listing}, ...] ) ]"""

    res = []
    walk('.', get_files, res)

    files = sorted([(x[2:].split('/'), join(x,y)) for x,y in res])
    del res

    results = []
    curr_cat = None
    table = []

    printed_exch_rate = False
    for file_ in files:
        cat = file_[0]
        if curr_cat != cat:
            if curr_cat:
                results.append([curr_cat, table])
                table = []

            curr_cat = cat
        
        filename = file_[1]
        file_ = file(file_[1]) 

        root = parse(file_).getroot()
        rows = root.cssselect("#table1 tr")[1:]

        exchange_rate = root.cssselect("table tr")[-1].cssselect("p")[0].text
        exchange_rate = exchange_rate.split("=")
        exchange_rate = map(unicode.strip, exchange_rate)

        assert exchange_rate[1][0] == "$"
        exchange_rate = float(exchange_rate[1][1:])

        if not printed_exch_rate:
            print "Exchange rate is:", exchange_rate
            printed_exch_rate = True
        

        for row in rows:
            children = row.getchildren()
            del children[-1]
            
            cells = []
            for cell in children:
                txt = cell.text
                if txt is None:
                    txt = cell.findtext("a")
                    if txt is None or txt == "":
                        txt = cell.getchildren()[1].text

                cells.append(txt)
            username = cells[2].split("(")
            if len(username) > 1:
                username[1] = username[1][:-1] # remove trailing )
            else:
                username.append('0')

            cells[2] = username[0] # the actual name
            cells.insert(3, username[1]) # the score
            row = {'name': cells[0], 
                   'price': cells[1], 
                   'username': cells[2], 
                   'user_score': cells[3], 
                   'country': cells[4]}
            table.append(row)

            price = row['price'].replace(u'฿', '').replace(',', '')
            price = float(price)
            row['price_bitcoins'] = price # in bitcoins
            row['price_dollars'] = price*exchange_rate

    results.append([curr_cat, table])
    return results

def get_csv(results):
    from StringIO import StringIO
    out = StringIO()
    writer = csv.writer(out, delimiter=',',quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['Category','Country','Price','User','User score', 'Name'])
    for result in results:
        cat = " - ".join(result[0])
        for row in result[1]:
            writer.writerow(map(lambda x: x.encode('utf-8'), (cat, row['country'], row['price'], row['username'], row['user_score'], row['name'])))

    return out.getvalue()


def collate_by_country(res):
    # Extract seen countries
    seen_in_data = []
    for r in res:
        for t in r[1]:
            name = t['country'].lower().replace("the", "").strip()
            seen_in_data.append(name)
    seen_in_data = frozenset(seen_in_data)

    countries_codes = frozenset((x['code'].lower() for x in countries))
    countries_names = frozenset((x['name'].lower() for x in countries))

    # Try to figure out the countries that were in this dataset and split them by recognition status
    recognized = []
    unrecognized = []
    recognition_map = {'united states of america': 'united states', 
                       'us, east coast': 'united states',
                       'usa': 'united states',
                       'east coast us': 'united states',
                       'east coast': 'united states',
                       'uk': "gb",
                       'finland, eu': 'finland',
                       'eu, nerlands': 'kingdom of the netherlands',
                       'nerlands': 'kingdom of the netherlands',
                       'aus': 'australia'}
    for d in seen_in_data:
        if d in recognition_map:
            d = recognition_map[d]

        if d not in countries_codes and d not in countries_names:
                unrecognized.append(d)
        else:
            country = [x for x in countries if x['name'].lower() == d or x['code'].lower() == d][0]
            recognized.append(country)

    recognized_values = [x['code'] for x in recognized] + \
                        [x['name'] for x in recognized]

    reverse_enumerate = lambda l: izip(xrange(len(l)-1, -1, -1), reversed(l))


    removed_items = 0
    results = deepcopy(res)
    old_items_count = sum(map(len, [x[1] for x in results]))
    for r in results:
        removed = len(r[1])
        for idx,x in reverse_enumerate(r[1]):
            if x['country'] not in recognized_values:
                del r[1][idx]
            else:
                x['country'] = [c for c in countries if c['code'] == x['country'] or c['name'] == x['country']][0]

        removed_items += removed - len(r[1])

    print "Removed", removed_items, "items"
    new_items_count = sum(map(len, [x[1] for x in results]))
    print "Unrecognized countries:", ", ".join(unrecognized)
    print "Retained %f" % (new_items_count/float(old_items_count))

    # Sanity check
    for r in results:
        for c in r[1]:
            assert c['country']['name'] in recognized_values

    # group the listings by country

    new_results = {}
    for r in results:
        drug_type = r[0][0] # ignore multiple levels and pick top-level only
        listings = {}
        for listing in r[1]:
            assert isinstance(listing, dict)
            assert len(listing['username']) > 0

            ccode = listing['country']['code'].upper() 
            if ccode in new_results:
                if drug_type in new_results[ccode]:
                    new_results[ccode][drug_type] += [listing]
                else:
                    new_results[ccode][drug_type] = [listing]
            else:
                new_results[ccode] = { drug_type: [listing] }


    stats = {}
    for ccode in new_results:
        st = {}
        listings = new_results[ccode]
        
        drug_counts = [(x, len(listings[x])) for x in listings]

        st['num_listings'] = sum([int(x[1]) for x in drug_counts])
        st['percent_all_listings'] = "%.2f%%" % (100*st['num_listings']/float(new_items_count))

        percentages = sorted(map(lambda (x,y): (x, 100*float(y)/st['num_listings']), drug_counts), key=itemgetter(1), reverse=True)
        percentages = map(lambda (x,y): "%s %.2f%%" %(x,y), percentages)
        st['drugs_distribution'] = percentages
        
        users = {}
        for drug in listings:
            for listing in listings[drug]:
                name = listing['username']
                if name not in users:
                    users[name] = 1
                else:
                    users[name] += 1

        users = [(x, 100*float(users[x])/st['num_listings']) for x in users]

        st['num_users'] = len(users)

        users = sorted(users, key=itemgetter(1), reverse=True)[:5]
        users = map(lambda (x,y): "%s %.2f%%" %(x,y), users)

        st['top_five_users'] = users

        stats[ccode] = st

    return stats

def collate_charts(results, countries_results):
    stats=[] 

    # calculate overall drug distribution (Cannabis combined)
    tmp = {}
    for r in results:
        key = r[0][0]
        if key in tmp:
            tmp[key] += len(r[1])
        else:
            tmp[key] = len(r[1])

    total_num = sum(tmp.itervalues())

    drugs = []
    for cat in tmp:
        drugs.append({ 'label': cat, 'data': tmp[cat]/float(total_num)})
    stats.append(("Drug types", drugs, 'pie'))

    # calculate distribution of cannabis sub-types
    cannabis = filter(lambda x: x[0][0] == "Cannabis", results)
    tmp = {}
    for r in cannabis:
        key = r[0][1]
        if key in tmp:
            tmp[key] += len(r[1])
        else:
            tmp[key] = len(r[1])

    total_cannabis = sum(tmp.itervalues())
    tmp = list(tmp.iteritems())
    tmp = sorted(tmp, key=itemgetter(1), reverse=True)

    drugs = []
    for cat, val in tmp:
        drugs.append({ 'label': cat, 'data': val/float(total_cannabis)})
    stats.append(("Cannabis types", drugs, 'pie'))

    # calculate percent of listings with country
    with_country = float(sum([x['num_listings'] for x in countries_results.itervalues()]))
    print "Listings with country:", with_country, "/", total_num
    stats.append(("Listings with country", [{'label': "With country", 'data': with_country/total_num}, 
                                            {'label': 'Without country', 'data': 1-(with_country/total_num)}], 'pie'));
    
    # calculate average price per category (cannabis split)
    tmp = [(r[0], len(r[1]), [x['price_dollars'] for x in r[1]]) for r in results if len(r[1]) > 0]
    tmp = [(r[0], sum(r[2])/float(r[1])) for r in tmp]
    
    tmp = sorted(tmp, key=itemgetter(1), reverse=True)
    drugs = []
    for idx, (drug, price) in enumerate(tmp):
        if len(drug) == 1: 
            drug = drug[0]
        else:
            drug = "%s (%s)" % (drug[0], " ".join(drug[1:]))

        price = round(price, 2) 
        drugs.append({ 'label': drug, 'data': [[idx, price]]})
    stats.append(("Average price per drug type (in USD)", drugs, 'bar'))
    
    # calculate top users overall (by listings)
    tmp = {}
    for r in results:
        for listing in r[1]:
            name = listing['username']
            country = listing['country']

            tup = (name, country)
            if tup not in tmp:
                tmp[tup] = 1
            else:
                tmp[tup] += 1

    tmp = sorted(list(tmp.iteritems()), key=itemgetter(1), reverse=True)[:10]
    users = []
    for idx, ((user, country), listings) in enumerate(tmp):
        label = "%s (%s)" %( user, country )

        users.append( {'label': label, 'data': [[idx, listings]]})
    stats.append(("Top sellers by # of listings", users, 'bar'))

    return stats

results = extract_results()
by_country = collate_by_country(results)
by_drugs = collate_charts(results, by_country)

template_countries = "stats_countries = %s"
template_drugs = "stats_drugs = %s"

with open('stats_countries.js', 'w') as f:
    f.write(template_countries % (json.dumps(by_country),))

with open('stats_drugs.js', 'w') as f:
    f.write(template_drugs % (json.dumps(by_drugs),))


