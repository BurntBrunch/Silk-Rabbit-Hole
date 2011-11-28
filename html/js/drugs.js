function pie_graph(holder, title, data, idx){
    var id = "graph-" + idx;
    var idHolder =  id + '-holder';
    var graphContainer = $('<span class="graph-container" id="' + id + '"><div class="title">' + 
                            title + '</div><div class="graph" id="' + idHolder + '"></div></span>');
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
        
        label.css({'z-index': maxZIdx});
        labelBackground.css({'z-index': maxZIdx});
    }

    graphHolder.bind("plothover", pieHover);
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
        }
    }
}
