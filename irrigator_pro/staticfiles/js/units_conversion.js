
/**
 * Convert all elements related to temperature based on the new value. Have to
 * make sure that the elements are in the old units.
 */



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

    $(".units_temp_form input").each(function() {
        var tmp = parseFloat($(this).val().trim());
        if (isNaN(tmp)) {
            return;
        }
        $(this).val(round_2(F(tmp)));
    });


    $(".units_temp").each(function() {
        var tmp = parseFloat($(this).text().trim());
        if (isNaN(tmp)) {
            return;
        }
        $(this).val(round_2(F(tmp)));
    });


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


    $(".units_depth_form input").each(function() {
        var tmp = parseFloat($(this).val().trim());
        if (isNaN(tmp)) {
            return;
        }
        $(this).val(round_2(tmp * mult));
    });

    $(".units_depth ").each(function() {
        var tmp = parseFloat($(this).text().trim());
        if (isNaN(tmp)) {
            return;
        }
        $(this).val(round_2(tmp * mult));
    });
}



$(document).ready(function() {
    $(".depth_units").change(function() {
        convert_depths($(this).attr("current-value"), $(this).val()); 
        $(this).attr("current-value", $(this).val());
    });


    $(".depth_units").each(function(){
        $(this).attr("current-value", $(this).val());
    });

});
