/** Use jQuery DatePicker widget for any data item **/
$(function() {
    $.datepicker.setDefaults({
	showButtonPanel: true,
	changeMonth: true,
	changeYear: true,
	dateFormat: 'yy-mm-dd',
	showMonthAfterYear: true,
	buttonImageOnly: false,
        buttonText: '<i class="fa fa-calendar"></i>',
	showOn:'button',
    });

    activateDatePicker()

    setNavigation();
});

function storeDate()
{
    this.stored_date = this.value;
    console.log( "value=" + this.value + "\n" + "stored_date=" + this.stored_date );
    
}

function activateDatePicker() {
    // Use date picker widget // Display calendar icon // Make narrower
    $('input[id$=date]').datepicker().css({
	"width":"7em",
	"margin": "2px" }).focus( storeDate )

    // Use datetime picker widget // Display calendar icon // Make narrower
    $('input[id$=datetime]').datetimepicker({timeFormat: "hh:mm:ss"}).css({
	"width": "12em",
	"margin": "2px"
    }).focus( storeDate )

    // Change defualt size of description and comment fields
    $('textarea[id$=description]').attr('rows',3)
    $('textarea[id$=comment]').attr('rows',3)
}


function setNavigation() {
    var debug = 0;

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
	        if(debug){ console.log("matched!") }
            $(this).closest('li').addClass('active');
        }
    });
}




/**
 * Function to create a valid id based on the data. Replaces everything that
 * is not an alpha-numeric with an underscore.
 */

function createValidID(oldString) {
    newString = oldString.replace(/\W/g, "_");
    console.log("Replacing " + oldString + " with " + newString);
    return newString;        
}





/**
 * Code copied from http://stackoverflow.com/questions/46155/validate-email-address-in-javascript
 *
*/

function validateEmail(email) {
    var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
    return re.test(email);
}
