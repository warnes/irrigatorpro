
/**
 * File to handle all the unit conversions in irrigator_pro.
 */

degF = '\xB0F';
degC = '\xB0C';

// Would be nicer with anonymous function. Just making sure it works for now.

function FtoC(f) {
    return (f-32.0) * 5.0 / 9.0;
}

function CtoF(c) {
    return 9.0 * c/5.0 + 32.0;
}

function round_2(v) {
    return Math.round((v + 0.00001) * 100) / 100;
}

function convert_temps(old_units, new_units) {
    
    if (old_units == new_units ) {
	/* no conversion necessary */
	return 
    } else if (old_units == "F" & new_units == "C") {
        conv = FtoC;
    } else if (old_units == "C" & new_units == "F") {
        conv = CtoF;
    } else {
	throw "Unknown conversion requested: " + old_units +  " to " + new_units 
    }

    $(".units_temp_input").each(function() {
        var tmp = parseFloat($(this).val().trim());
        if (isNaN(tmp)) {
            return;
        }
        $(this).val(round_2(conv(tmp)));
    });


    // $(".units_temp").each(function() {
    //     var tmp = parseFloat($(this).text().trim());
    //     if (isNaN(tmp)) {
    //         return;
    //     }
    //     $(this).val(round_2(F(tmp)));
    // });


}


/**
 * Convert between inches and back
 */

function convert_depths(old_units, new_units) {

    var mult;

    if (old_units == new_units ) {
	/* no conversion necessary */
	return 
    } else if (old_units == "in" & new_units== "cm" ) { 
        mult = 2.54; 
    } else if (old_units == "in" & new_units == "mm") {
        mult = 25.4; 
    } else if (old_units == "cm" & new_units == "in") {
        mult = 0.3937008; 
    } else if (old_units == "cm" & new_units == "mm") {
            mult = 10.0
    } else if (old_units == "mm" & new_units == "in") { 
        mult = 0.03937008;
    } else if (old_units == "mm" & new_units == "cm") {
            mult = 0.1; 
    } else {
	throw "Unknown conversion requested: " + old_units +  " to " + new_units 
    }

    $(".units_depth_input").each(function() {
        var tmp = parseFloat($(this).val().trim());
        if (isNaN(tmp)) {
            return;
        }
        $(this).val(round_2(tmp * mult));
    });

}


function change_temp_headers(new_temp) {
    replace_with = degC;
    if (new_temp == "F") {
        replace_with = degF;
    }

   $(".temp_header").each(function() {
        $(this).text($(this).text().replace(/\s*\(.+\)\s*$/, " (" + replace_with + ")"));
    });
}


function change_header_units(new_units) {

    $(".depth_header").each(function() {
        $(this).text($(this).text().replace(/\s\(\w+\)\s*$/, " (" + new_units + ")"));
    });

}


$(document).ready(function() {
    
    $(".depth_units").change(function() {

        /**
         * Change the values in the cells, saving the new units so we know
         * what it is next time there is a change.
         */
        convert_depths($(this).attr("current-value"), $(this).val());
        change_header_units($(this).val());
        $(this).attr("current-value", $(this).val());
	Cookies.set("depth_units", $(this).val()); // Store in cookie
    });


    $(".temp_units").change(function() {
        convert_temps($(this).attr("current-value"), $(this).val());
        change_temp_headers($(this).val());
	$(this).attr("current-value", $(this).val());
	Cookies.set("temp_units", $(this).val()); // Store in cookie
    });
    

    /**
      Convert units to inches and Farenheit for submit 
    **/
    $("form#formset").submit(function(){
	convert_depths( $(".depth_units").val(), "in");
	convert_temps(  $(".temp_units").val(),  "F");
    });


    /** 
      Set initial column unit labels
     **/
    $(".depth_header").each(function() {
	$(this).text($(this).text() + " (in)");
    });        

    $(".temp_header").each(function() {
	$(this).text($(this).text() + " (" + degF + ")" );
    });        


    /**
     * Pull default units from Cookie, if present, defaulting to inches & Farenheit. 
     * Should modify to start based on specific object. Related to next comment.
     */

    if( Cookies.set("depth_units") == "cm") {
	$(".depth_units").val("cm");
	change_header_units("cm");
	convert_depths("in","cm");
    } else if( Cookies.set("depth_units") == "mm") {
	$(".depth_units").val("mm");
	change_header_units("mm");
	convert_depths("in","mm");
    } else { 
	change_header_units("in");
	$(".depth_units").val("in");
    }

    if( Cookies.get("temp_units") == "C" ) {
	$(".temp_units").val("C");
	change_temp_headers($(this).val());
	convert_temps("F","C");
    } else { 
	$(".temp_units").val("F");
	change_temp_headers($(this).val());
    }


    /**
     * TODO This will apply to all elements in the same page. May want to
     * modify if we want more than one element in a page to use the same
     * class.
     */

    $(".depth_units").each(function(){
        $(this).attr("current-value", $(this).val());
    });

    $(".temp_units").each(function(){
        $(this).attr("current-value", $(this).val());
    });


    /**
     * Create a hidden input with the form id when a input is
     * clicked. This is required to prevent all forms from being saved
     * each time the units are being converted.
     *
     * In the form the textarea for the comment does not use
     * the input tag.
     */
    
    $('form input, form textarea').change( function() {

        /**
         * Only use if if id has either the pattern: 
         *      id_form-(\d+).*
         * or
         *      manual-entry-time-(\d+)*
         * 
         * The matched number indicates the form index
         */
        
        var pattern1 = new RegExp("id_form-(\\d+)");
        var pattern2 = new RegExp("manual-entry-time-(\\d+)");

        var res = pattern1.exec($(this).attr("id"));
        
        if (res == null)
            res = pattern2.exec($(this).attr("id"));

        if (res == null) {
            console.log("No match");
            return;
        }
        //console.log("Matched for form: " + res[1]);
        form_id = "id_form-" + res[1] + "-id";
        
        // Add the form id to hidden input

        var add_to_form = true;
        $('.changed_forms').each(function(){
            if ($(this).val() == form_id) {
                add_to_form = false;
            }
        });

        if (add_to_form) {
            $('<input>').attr({
                class: 'changed_forms',
                type: 'hidden',
                name: "changed_forms[]",
                value: form_id}).appendTo($(this).closest('form'));
        } else {
        }
    });
});
