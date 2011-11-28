function setup_links()
{
    var links = $("#menu a");
    var pages = $(".page");
    
    var currentPage = 0;

    links.each(function (idx, val){
        $(val).click(function(){
            $(pages[currentPage]).fadeOut('fast', function(){
                $(pages[idx]).fadeIn('fast');
                currentPage = idx;
            });
        });
    });
    pages.hide();
    pages.first().fadeIn('fast');
    //pages.last().show();
}
