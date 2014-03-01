$(function () {
    setNavigation();
});

function setNavigation() {
    var debug = 0;

    var path = window.location.pathname;

    // trim any # page references
    path = path.replace(/#.*$/,"");

    // trim any trailing slash
    if( path > "/")
	path = path.replace(/\/$/, "");


    path = decodeURIComponent(path);

    if(debug){  console.log("path=" + path ); }

    $(".nav a").each(function () {
        var href = $(this).attr('href');
	
	// Trim trailing slash
	if( href > "/")
	    href = href.replace(/\/$/, "");

	if(debug) { console.log("href='" + href + "', length=" + href.length ); }

	if( (path==="/" && href==="/") || 
	    (href.length > 1 && path.substring(0, href.length) === href) )
	{
	    console.log("matched!")
            $(this).closest('li').addClass('active');
        }
    });
}


/** Use jQuery DatePicker widget for any data item **/
$(function() {
    $.datepicker.setDefaults({
	showButtonPanel: true, 
	changeMonth: true, 
	changeYear: true,
	dateFormat: 'yy-mm-dd', 
	showMonthAfterYear: true,
    });
    
    $('input[id$=date]').datepicker(); // Use date picker widget
    $('input[id$=date]').wrap('<i class="fa fa-calendar"></i>'); // Display calendar icon
    $('input[id$=date]').width("3em") // -= $(".fa").width();    // Make narrower 

    $('input[id$=datetime]').datetimepicker(); // Use date picker widget
    $('input[id$=datetime]').wrap('<i class="fa fa-calendar"></i>'); // Display calendar icon
    $('input[id$=datetime]').width("6em") // -= $(".fa").width();    // Make narrower 
});

