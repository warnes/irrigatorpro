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
      $('input[id$=date]').datepicker({ dateFormat: 'yy-mm-dd' }); // Use date picker widget
      $('input[id$=date]').wrap('<i class="fa fa-calendar"></i>'); // Display calendar icon
      $('input[id$=date]').width("3em") // -= $(".fa").width();    // Make narrower 
    });




/** Use jQuery-ui-datetimepicker-addon DateTimePicker widget for any datatime item **/
$(function() {
      $('input[id$=datetime]').datetimepicker({ dateFormat: 'yy-mm-dd' }); // Use date picker widget
      $('input[id$=datetime]').wrap('<i class="fa fa-calendar"></i>'); // Display calendar icon
      $('input[id$=datetime]').width("6em") // -= $(".fa").width();    // Make narrower 
    });

