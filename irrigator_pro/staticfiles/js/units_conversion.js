
/**
 * File to handle all the unit conversions in irrigator_pro.
 */


degF = '\xB0F';
degC = '\xB0C';



// Would be nicer with anonymous function. Just making sure it works for now.

function toCelsius(f) {
    return (f-32.0) * 5.0 / 9.0;
}

function toFarenheit(c) {
    return 9.0 * c/5.0 + 32.0;
}


function round_2(v) {
    return Math.round((v + 0.00001) * 100) / 100;
}

function convert_temps() {

    if ($("#temp_units").val() == "C") {
        F = toCelsius;
    } else {
        F = toFarenheit;
    }

    $(".units_temp_input").each(function() {
        var tmp = parseFloat($(this).val().trim());
        if (isNaN(tmp)) {
            return;
        }
        $(this).val(round_2(F(tmp)));
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
    if (old_units == "in") {
        mult = 2.54; // Converting in to cm
        if (new_units == "mm") {
            mult = 25.4; // Converting in to mm
        }
    } else if (old_units == "cm") {
        mult = 0.3937008; // Converting cm to in
        if (new_units == "mm") {
            mult = 10.0
        }
    } else { // old_units == mm
        mult = 0.03937008; // Converting mm to in
        if (new_units == "cm") {
            mult = 0.1; // Converting mm to cm
        }
    }

    // /**
    //  * Convert values used inform
    //  */
    // $(".units_depth_form input").each(function() {
    //     var tmp = parseFloat($(this).val().trim());
    //     if (isNaN(tmp)) {
    //         return;
    //     }
    //     $(this).val(round_2(tmp * mult));
    // });

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
        $(this).text($(this).text().replace(/\(.+\)\s*$/, "(" + replace_with + ")"));
    });
}



function change_header_units(new_units) {

    $(".depth_header").each(function() {
        $(this).text($(this).text().replace(/\(\w+\)\s*$/, "(" + new_units + ")"));
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
    });


    $(".temp_units").change(function() {
        convert_temps();
        change_temp_headers($(this).val());
    });


    /**
     * TODO This will apply to all elements in the same page. May want to
     * modify if we want more than one element in a page to use the same
     * class.
     */

    $(".depth_units").each(function(){
        $(this).attr("current-value", $(this).val());
    });

    /**
     * TODO Hardcoded to start with inches. Should modify to start based
     * on specific object. Related to above comment.
     */
    $(".depth_header").each(function() {
        $(this).text($(this).text() + " (in)");
    });

    $(".temp_header").each(function() {
        $(this).text($(this).text() + "(" + degF + ")");
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
        

        console.log("Clicked for form: " + $(this).attr("id"));
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