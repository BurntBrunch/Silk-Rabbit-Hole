function pie_graph(holder, title, data, idx){
    var id = "graph-" + idx;
    var idHolder =  id + '-holder';
    var graphContainer = $('<span class="graph-container-pie" id="' + id + '"><div class="title">' + 
                            title + '</div><div class="graph-pie" id="' + idHolder + '"></div></span>');
    holder.append(graphContainer);

    var graphHolder = $("#" + idHolder);
        
    $.plot(graphHolder, data, 
        { series: { pie: {
                           show: true,
                           radius: 0.8,
                           innerRadius: 0.3,
                           label: {
                                formatter: function(label, series){
                                return '<div style="font-size:8pt;text-align:center;padding:4px;">'+label+'<br/>'+Math.round(series.percent)+'%</div>';
                                },
                                radius: 1,
                                background: { opacity: 0.8 },
                           }
                          } 
                 }, 
          legend: { show: false },
          grid: {
              hoverable: true,
              clickable: true
            }
    });

    var maxZIdx = 99;
    
    function pieHover(evt, pos, obj){
        if(!obj)
            return;
        
        // The purpose of this handler is to re-order the labels, so that
        // hovering on one of areas changes the z-index of the appropriate
        // label`

        var labelId = obj.seriesIndex;
        labelId = "pieLabel" + labelId;
        
        // This part is a bit flaky and it relies on the way Flot puts
        // elements in the DOM - the background would be the previous
        // sibling of the label's text 
        var label = graphContainer.find("#" + labelId);
        var labelBackground = label.prev();

        maxZIdx++;

        // Bring the label to the top
        label.css({'z-index': maxZIdx});
        labelBackground.css({'z-index': maxZIdx});
    }

    graphHolder.bind("plothover", pieHover);
}

function bar_graph(holder, title, data, idx){
    var id = "graph-" + idx;
    var idHolder =  id + '-holder';
    var graphContainer = $('<span class="graph-container-bar" id="' + id + '"><div class="title">' + 
                            title + '</div><div class="graph-bar" id="' + idHolder + '"></div></span>');
    holder.append(graphContainer);

    var graphHolder = $("#" + idHolder);
        
    $.plot(graphHolder, data, 
        { series: { bars: {
                           show: true,
                           align: 'center',
                           horizontal: false,
                          } 
                 }, 
          legend: { show: false },
          xaxis: {
              tickFormatter: function(idx){
                    if(idx >= 0 && idx < data.length){
                        var spaceEvery = 8,
                            t = data[idx].label,
                            len = t.length,
                            spacesToInsert = len/spaceEvery,
                            spacesInserted = 0,
                            space = "<br>";

                        if( spacesToInsert >= 1){
                            for(var i=i; i<=spacesToInsert; i++){
                                var pos = i*spaceEvery + 
                                    spacesInserted*space.length;
                                t = t.slice(0, pos) + space + t.slice(pos);
                                spacesInserted++;
                            }
                        }
                        return t;
                    }
                    return "";
                  },
                  ticks: data.length,
                  tickDecimals: 1,
                  tickLength: 20,
                  tickColor: '#999',
                  minTickSize: 1,
          },
          grid: {
              hoverable: true,
              clickable: true
            }
    });

    var logged = false;
    function barHover(evt, pos, obj){
        graphHolder.children().filter('.popup').remove();
        if(!logged){
            console.log(graphHolder);logged=true;}

        if(!obj)
            return;

        var popup = $('<span class="popup">' + obj.datapoint[1] + '</span>');

        graphHolder.append(popup);
    }
    graphHolder.bind("plothover", barHover);
}

function setup_drugs(){
    var holder = $("#stats");

    for(var k in stats_drugs){
        var graph = stats_drugs[k];

        var title = graph[0];
        var data = graph[1];
        var type = graph[2];
        
        if(type == "pie"){
            pie_graph(holder, title, data, k);
        } else if (type == "bar"){
            bar_graph(holder, title, data, k);
        }
    }
}
