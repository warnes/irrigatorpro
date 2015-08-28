function storeDate()
{
    this.stored_date = this.value;
    //console.log( "value=" + this.value + "\n" + "stored_date=" + this.stored_date );
    
}

function activateDatePicker() {
    // Use date picker widget // Display calendar icon // Make narrower
    $("input[id$=date]").not('form input:hidden').not('.hidden').datepicker().css({
	"width":"7em",
	"margin": "2px" }).focus( storeDate )

    // Use datetime picker widget // Display calendar icon // Make narrower
    $("input[id$=datetime]").not('form input:hidden').not('.hidden').not('.readonly').datetimepicker({timeFormat: "HH:mm:ss"}).css({
	"width": "12em",
	"margin": "2px"
    }).focus( storeDate )

    // Change defualt size of description and comment fields
    $("textarea[id$=description]").attr("rows",3)
    $("textarea[id$=comment]").attr("rows",3)
}


function setNavigation() {
    var debug = 0;
    console.log("setNavigation called");
    var path = window.location.pathname;

    // trim any # page references
    path = path.replace(/#.*$/,"");

    // trim any trailing slash
    if( path > "/")
	path = path.replace(/\/$/, "");

    // trim leading "farm/"
    path = path.replace(/^\/farm/, "");

    path = decodeURIComponent(path);

    if(debug){  console.log("path=" + path ); }

    $(".nav a").each(function () {
        var href = $(this).attr("href");

	// Trim trailing slash
	if( href > "/")
	    href = href.replace(/\/$/, "");


	// trim leading "/farm"
	href = href.replace(/^\/farm/, "");

	if(debug) { console.log("href='" + href + "', length=" + href.length ); }

	if( (path==="/" && href==="/") ||
	    (href.length > 1 && path.substring(0, href.length) === href) )
	{
	        if(debug){ console.log("matched!") }
            $(this).closest("li").addClass("active");
        }
    });
}




/**
 * Function to create a valid id based on the data. Replaces everything that
 * is not an alpha-numeric with an underscore.
 */

function createValidID(oldString) {
    newString = oldString.replace(/\W/g, "_");
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

function extractEmail(queryString) {
    var re = /[\w-]+(?:\.[\w-]+)*@(?:[\w-]+\.)*\w[\w-]{0,66}\.[a-z]{2,6}(?:\.[a-z]{2})?/i;
    var pattern = new RegExp(re);
    var m = pattern.exec(queryString);
    if (m == null)
	return "";
    return m[0];
}

/****
 * Calculate number of days between two dates, adpated from
 * stackoverflow and google. 
 ****/
function daysBetween(firstDate, secondDate) {
    var oneDay = 24*60*60*1000; // hours*minutes*seconds*milliseconds
    return   Math.round((secondDate.getTime() - firstDate.getTime())/(oneDay));
}


/****
 * Filter crop seasons shown on the navbar  based on value of "season"
 * selector (defaulting to "current")
 ****/
function filter_item() {
    if( $("select#show_all_seasons").val()=="all" ) {
	$(this).show();
    } else {
	start_date = moment( $(this).attr("start_date") ).subtract(1, 'months');
	end_date   = moment( $(this).attr("end_date")   ).add     (1, 'months');
	now = moment();
	//console.log(start_date + " through " + end_date);
	if( now > start_date & 
	    now < end_date     ){
	    $(this).show();
	    //console.log("showing" + start_date + " through " + end_date);
	} else {
	    $(this).hide();
	    //console.log("hiding" + start_date + " through " + end_date);
	}
    }
}

function filter_seasons() {
    // Do the filtering
    $("[start_date]").each(filter_item);

    // Store the new value of show_all_seasons as a cookie.
    Cookies.set("show_all_seasons", $("select#show_all_seasons").val() );
}

/**********************/
/** Run on page load **/
/**********************/
$(function() {
    /** Use jQuery DatePicker widget for any data item **/
    $.datepicker.setDefaults({
	showButtonPanel: true,
	changeMonth: true,
	changeYear: true,
	dateFormat: "yy-mm-dd",
	showMonthAfterYear: true,
	buttonImageOnly: false,
        buttonText: '<i class="fa fa-calendar"></i>',
	showOn:"button",
    });

    activateDatePicker();

    setNavigation();

    // Make as readonly all input elements within object with class readonly.
    //$(".readonly").find(":input").attr("readonly","readonly").
    // addClass("readonly");
    $(".readonly").
	find(":input").
	not("[id$=comment]").
	attr("readonly","readonly").
	addClass("readonly");

    // Set the value of show_all_seasons from a cookie (if present)
    if( Cookies.get("show_all_seasons") == "all") {
	$("select#show_all_seasons").val("all");
    } else {
	$("select#show_all_seasons").val("current");
    }

    // Run filter on seasons 
    filter_seasons()

   $("select").not(".exclude-chosen").chosen({disable_search_threshold: 5});
});
