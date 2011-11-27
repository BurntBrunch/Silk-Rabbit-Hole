function setup_links()
{
    var links = $("#menu a");
    var pages = $(".page");

    links.each(function (idx, val){
        $(val).click(function(){
            pages.fadeOut('fast', function(){
                $(pages[idx]).fadeIn('fast');
            });
        });
    });
}
