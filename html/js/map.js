function setup_map() {
    function scale_map(map, sx, sy){
        for(k in map){
            map[k].scale(sx, sy);
        }
    }
    function set_panel(ccode){
        var panel = $("#panel");
        panel.children().remove();
    
        country = code_country[ccode.toUpperCase()];
        var panel_title = $('<h2 id="panel-country">' + country.toLowerCase() + '</h2>');
        panel.append(panel_title);

        append_country_stats(panel, ccode);
        panel.fadeIn('fast');
    }
    var attr = {
        fill: "#333",
        stroke: "#666",
        "stroke-width": .5,
        "stroke-linejoin": "round"
    };
    
    var map = {};
    var R = Raphael("holder", 1000, 500);
    render_map(R,map,attr);
    function resizePaper(){
        var win = $(this);
        var paper = $("#holder");

        R.setSize(paper.width(), paper.width()/2, true, false);
        R.setViewBox(0,0,1000, 500, true);
    }
    resizePaper();
    $(window).resize(resizePaper); 

    function clear_state(st){
        if(st != null)
        {
            st.animate({opacity: 0.25}, 300);
            R.safari();
        }
    }
    
    var clicked_state = null;
    for (var state in map) {							        
        if(state in stats_countries){
            map[state].color = Raphael.getColor();
            (function (st, state) {
                st[0].style.cursor = "pointer";
                var bbox = st.getBBox();
                st[0].midx = bbox.x + bbox.width/2;
                st[0].midy = bbox.y + bbox.height/2;
                st.animate({opacity: 0.25, fill: st.color, stroke: '#ccc'}, 500);

                st[0].onmouseover = function () {
                    st.animate({opacity: 1}, 300);
                    R.safari();
                };
                st[0].onmouseout = function () {
                    if(st != clicked_state)
                        clear_state(st);
                };
                
                st[0].onclick = function () {
                    if(st != clicked_state)
                    {
                        clear_state(clicked_state);
                        set_panel(state);
                        clicked_state = st;
                    }
                };
            })(map[state], state);
        }
    }; // end for
    
    

    function lon2x(lon) {
        var xfactor = 2.6938;
        var xoffset = 465.4;
        var x = (lon * xfactor) + xoffset;
        return x;
    }
    function lat2y(lat) {
        var yfactor = -2.6938;
        var yoffset = 227.066;
        var y = (lat * yfactor) + yoffset;
        return y;
    }
}
