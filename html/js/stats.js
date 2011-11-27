function append_country_stats(holder, ccode){
    if(holder){
        elem = $(holder);
        
        var html = "";
        if(ccode in stats_countries){
            var cstats = stats_countries[ccode];

            for(var cstat in stats_country_order){
                cstat = stats_country_order[cstat];
                var val = cstats[cstat];
                var title = stats_country_names[cstat];

                html += "<h6>" + title + "</h6><ul>";
                if (val instanceof Array){
                    for (var key in val)
                        html += "<li>" + val[key] + "<br />";
                } else 
                    html += "<li>" + val + "<br />";
                
                html += "</ul>";
            }
        }
        elem.append($(html));
    }
}
