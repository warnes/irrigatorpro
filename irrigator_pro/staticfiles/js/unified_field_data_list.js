// Some global variables. Will be assigned in $(document).ready()

var start_date;
var end_date;


var showCompleteText = "Show Entire Season";	
var showLast15Text   = "Show &plusmn;7 Days"	


function addRow(afterRowID, date, crop_season_pk) {

    // Get number of current forms. Will have to update this count,
    // 

    var nb_current_forms = $("#id_form-TOTAL_FORMS").val()
    console.log(nb_current_forms)

    
    // var sFormat = "My name is {0} and I am version {1}.0.";
    // var result = bob.string.formatString(sFormat, "Bob", 1);
    // console.log(result);

    var newRowFormat=
        "<tr id='new-{0}'>" +
        "<td>" + date + "<input id='id_form-{0}-date' name='form-{0}-date' type='hidden' value='" + date + "' />"  + 
        "<input id='id_form-{0}-crop_season' name='form-{0}-crop_season' type='hidden' value='" + crop_season_pk + "' />" +
        "</td>" +
        "<td>Manual Entry</td>" +
        "<td><input id='id_form-{0}-soil_potential_8' name='form-{0}-soil_potential_8' step='0.01' type='number' /></td>"+
        "<td><input id='id_form-{0}-soil_potential_16' name='form-{0}-soil_potential_16' step='0.01' type='number' /></td>" +
        "<td><input id='id_form-{0}-soil_potential_24' name='form-{0}-soil_potential_24' step='0.01' type='number' /></td>" +
        "<td><input id='id_form-{0}-min_temp_24_hours' name='form-3-min_temp_24_hours' step='0.01' type='number' /></td>" +
        "<td><input id='id_form-{0}-max_temp_24_hours' name='form-3-max_temp_24_hours' step='0.01' type='number' /></td>" +
        "<td><input id='id_form-{0}-rain' name='form-{0}-rain' step='0.01' type='number'  value='0'/></td>" +
        "<td><input id='id_form-{0}-irrigation' name='form-{0}-irrigation' step='0.01' type='number' value='0'  /></td>" +
        "<td><input id='id_form-{0}-ignore' name='form-{0}-ignore' type='checkbox'/></td>" +
        "</tr>";

    // From bob.js package
    var newRow = bob.string.formatString(newRowFormat, nb_current_forms);
    console.log(newRow);

    $("#id_form-TOTAL_FORMS").val(parseInt(nb_current_forms)+1)
    //$("input[id=id_form-TOTAL_FORMS]").val(parseInt(nb_current_forms)+1)
    $("#" + afterRowID).after(newRow)
}


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

function convert_depths() {

    var mult = 0.3937008;
    if ($("#depth_units").val() == "cm") {
        mult = 2.54;
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



/**
 * Color the rows based on today's date.
 */



function colorPastTodayFuture() {

    var reportDateVal = $.datepicker.parseDate('yy-mm-dd', $("#datepicker").val() );

    $(".data_row").each( function() {
        thisDate= $.datepicker.parseDate('yy-mm-dd', $(this).attr("data-for-date"));

        if (daysBetween(reportDateVal, thisDate) < 0) {
            $(this).addClass("row-past");
        }
        else if (daysBetween(reportDateVal, thisDate) == 0) {
            $(this).addClass("row-today");
        }
        else if (daysBetween(reportDateVal, thisDate) > 0) {
            $(this).addClass("row-future");
        }
    });
}


$(document).ready(function() {


    $("input[id$=reading_time]").timepicker({
        timeFormat: 'HH:mm'
    });



    start_date = getStartDate();
    end_date = getEndDate();


    /**
     * Disable datepicker since it is only used as a hidden input in a
     * form.
     */
    
    $('form input:hidden').each(function() {
        // Could be more refined and only destroy
        // on date fields, but there doesn't seem
        // to be an issue here.
        $(this).datepicker('destroy');
    });




    // Initial settings for the number of rows to show
    $("#rows_option").html(showCompleteText);
    show15();
       	
    // Apply toggle to table
    $("#rows_option").click(
       	function() {
       	    if ($(this).html() == showCompleteText) {
       		$("#rows_option").html(showLast15Text);
       		showAll();
       	    } else {
        	$("#rows_option").html(showCompleteText);
       		show15();
       	    }
       	}
    );





    /**
     * Create a hidden input with the form id when a input is
     * clicked. This is required to prevent all forms from being saved
     * each time the units are being converted.
     */
    
    $('form input').click( function() {

        // Only use if if id has the form: id_form-\d+.*, in which case we only
        // name of the form is id_form_\d+-id.
        
        // Could make this one static...
        var pattern = new RegExp("id_form-\\d+");
        var res = pattern.exec($(this).attr("id"));
        
        if (res == null)
            return;
        form_id = res[0] + "-id";
        
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



    /**
     * Remove the type=number from the rain and irrigation, and put them back
     * just before form is submitted.
     *
     * Would work, have not tested setting back to number on submit.
     */


    // $(".units_temp_form input").each(function() {
    //     $(this).removeAttr("type");

    // });
    
    $(".dti").each(function() {
    	
    	var contents = $(this).text();
    	
    	if (contents.indexOf("Dry-") > 0) {
    	    
    	    $(this).children().first().addClass("alert-inline alert-info");
    	} else if (contents.indexOf("Today") > 0) {
    	    
    	    $(this).children().first().addClass("alert-inline alert-danger");
    	} else if (contents.indexOf("Tomorrow") > 0) {
    	    
    	    $(this).children().first().addClass("alert-inline alert-warning");
    	} else {
    	    number = contents.replace(/\D/g, '');
    	    if (number != "") {
    		
    		if (number < 4) {
    		    $(this).children().first().addClass("alert-inline alert-warning");
    		} else {
    		    $(this).children().first().addClass("alert-inline alert-success");
    		}
    		
    	    }
    	}
    	
    	
    });


    /**
     * Create an event for the text inputs containing a temperature
     * changes. If it ends with [fF] or [cC] will convert depending on what
     * the form says.
     *
     * Will only chage if matches reg
     *  (valid_float)\s*[fFcF]
     *
     * and will convert if necessary, remove last character
     */

    // This till not work as long as the type in the input in 'number'

    // $(".units_temp_form input").focusout(function() {


    //     $(this).removeAttr("type");
            

    //     var regex = /(\d+)\s*([cCfF])$/g;
    //     var text = $(this).val().trim();

    //     console.log("Executing on: ", text);

    //     result = regex.exec(text);

    //     console.log(result);

    //     $(this).attr("type", "number");

    //     // var tmp = parseFloat($(this).val().trim());
    //     // if (isNaN(tmp)) {
    //     //     return;
    //     // }
    //     // $(this).val(round_2(F(tmp)));
    // });


    $("table.unified-table").floatThead({
        scrollingTop:50
    });
});


function showAll() {
    $(".data_row").css("display", "");

    colorPastTodayFuture();

    // Recalculate column widths for floating header
    $("table.unified-table").floatThead('reflow');
}


function dateChangedManually() {
    	
    var newDate;
    try {
    	newDate = $.datepicker.parseDate('yy-mm-dd', $("#datepicker").val());
    	$("#date-error").css("display", "none");
    } catch (e) {
    	$("#date-error").css("display", "inline");
    	return;
    }
    
    if( newDate < startDate || newDate > endDate )
    {
        $("#date-error").css("display", "inline");
        return; 
    }
    
    show15();
    
}




function show15() {
    var reportDateVal = $.datepicker.parseDate('yy-mm-dd', $("#datepicker").val() );

    $(".data_row").each(function() {
        thisDate= $.datepicker.parseDate('yy-mm-dd', $(this).attr("data-for-date"));
    	if ( Math.abs(daysBetween(reportDateVal, thisDate)) <= 7) {
    	    $(this).css("display","");
        } 
        else {
    	    $(this).css("display","none");
        } 
    });
 
    colorPastTodayFuture();

    // Recalculate column widths for floating header   	
    $("table.unified-table").floatThead('reflow');
}