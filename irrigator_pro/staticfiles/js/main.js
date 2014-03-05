/** Use jQuery DatePicker widget for any data item **/
$(function() {
    $.datepicker.setDefaults({
	showButtonPanel: true, 
	changeMonth: true, 
	changeYear: true,
	dateFormat: 'yy-mm-dd', 
	showMonthAfterYear: true,
    });
    
    // Use date picker widget // Display calendar icon // Make narrower 
    $('input[id$=date]').datepicker().wrap('<i class="fa fa-calendar"></i>').css({ 
	"width":"7em", 
	"margin": "2px" })

    // Use datetime picker widget // Display calendar icon // Make narrower 
    $('input[id$=datetime]').datetimepicker().wrap('<i class="fa fa-calendar"></i>').css({
	"width": "12em",
	"margin": "2px"
    }) 

    // Change defualt size of description and comment fields 
    $('textarea[id$=description]').attr('rows',3)
    $('textarea[id$=comment]').attr('rows',3)

});


function setNavigation() {
    var debug = 1;

    var path = window.location.pathname;

    // trim any # page references
    path = path.replace(/#.*$/,"");

    // trim any trailing slash
    if( path > "/")
	path = path.replace(/\/$/, "");

    // trim leading 'farm/'
    path = path.replace(/^\/farm/, "");

    path = decodeURIComponent(path);

    if(debug){  console.log("path=" + path ); }

    $(".nav a").each(function () {
        var href = $(this).attr('href');
	
	// Trim trailing slash
	if( href > "/")
	    href = href.replace(/\/$/, "");


	// trim leading '/farm'
	href = href.replace(/^\/farm/, "");

	if(debug) { console.log("href='" + href + "', length=" + href.length ); }

	if( (path==="/" && href==="/") || 
	    (href.length > 1 && path.substring(0, href.length) === href) )
	{
	    console.log("matched!")
            $(this).closest('li').addClass('active');
        }
    });
}

$(function () {
    setNavigation();
});
