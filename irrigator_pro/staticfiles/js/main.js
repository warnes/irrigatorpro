$(function () {
    setNavigation();
});

function setNavigation() {
    var path = window.location.pathname;
    path = path.replace(/#.*$/,"");
    if( path > "/")
	path = path.replace(/\/$/, "");
    path = decodeURIComponent(path);
    console.log("path=" + path );

    $(".nav a").each(function () {
        var href = $(this).attr('href');

	console.log("href='" + href + "', length=" + href.length );

	if( (path==="/" && href==="/") || 
	    (href.length > 1 && path.substring(0, href.length) === href) )
	{
	    console.log("matched!")
            $(this).closest('li').addClass('active');
        }
    });
}



