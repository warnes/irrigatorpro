// Some global variables. Will be assigned in $(document).ready()

var start_date;
var end_date;


var showCompleteText = "Show Entire Season";	
var showLast15Text   = "Show &plusmn;7 Days"	


function addRow(afterRowID, date, time, crop_season_pk) {

    // Get number of current forms. Will have to update this count,
    // 

    var nb_current_forms = $("#id_form-TOTAL_FORMS").val()

    if(time <= ''){
	time = moment().format("HH:mm")
    }

    var datetime = date + " " + time;
    
    var newRowFormat=
        '<tr id="new-{0}">' +
        '<td>' + date + '<input id="id_form-{0}-date" name="form-{0}-date" type="hidden" value="' + date + '" />'  + 
        '<input id="id_form-{0}-crop_season" name="form-{0}-crop_season" type="hidden" value="' + crop_season_pk + '" />' +
        '<input id="id_form-{0}-source" name="form-{0}-source" type="hidden" value="User" />' +
        '</td>' +
        '<td><input id="id_form-{0}-time" name="form-{0}-time" value="' + time + '"/></td>' +
        '<td>Manual Entry</td>' +
        '<td><input id="id_form-{0}-soil_potential_8" name="form-{0}-soil_potential_8" step="0.01" type="number" /></td>'+
        '<td><input id="id_form-{0}-soil_potential_16" name="form-{0}-soil_potential_16" step="0.01" type="number" /></td>' +
        '<td><input id="id_form-{0}-soil_potential_24" name="form-{0}-soil_potential_24" step="0.01" type="number" /></td>' +
        '<td><input id="id_form-{0}-min_temp_24_hours" name="form-{0}-min_temp_24_hours" step="0.01" type="number" /></td>' +
        '<td><input id="id_form-{0}-max_temp_24_hours" name="form-{0}-max_temp_24_hours" step="0.01" type="number" /></td>' +
        '<td><input id="id_form-{0}-rain" name="form-{0}-rain" step="0.01" type="number"  value="0"/></td>' +
        '<td><input id="id_form-{0}-irrigation" name="form-{0}-irrigation" step="0.01" type="number" value="0"  /></td>' +
        '<td><input id="id_form-{0}-ignore" name="form-{0}-ignore" type="checkbox"/></td>' +
	'<td><input id="id_form-{0}-datetime" name="form-{0}-datetime" type="hidden" value="' + datetime + '"/> </td>' +
	'<td></td>' +
	'<td></td>' +
	'<td></td>' +
	'<td></td>' +
	'<td><textarea cols="40" id="id_form-{0}-comment" name="form-{0}-comment" rows="3"></textarea></td>' +
        '</tr>';

    // From bob.js package
    var newRow = bob.string.formatString(newRowFormat, nb_current_forms);
    console.log("new row: " + newRow);

    $("#id_form-TOTAL_FORMS").val(parseInt(nb_current_forms)+1)
    //$("input[id=id_form-TOTAL_FORMS]").val(parseInt(nb_current_forms)+1)
    $("#" + afterRowID).after(newRow)

    selectString = bob.string.formatString("#id_form-{0}-time", nb_current_forms);

    $(selectString).datetimepicker({
	timeOnly:true,
	buttonText: '<i class="fa fa-clock-o"></i>',
	format:'H:i'
    })
    $(selectString).css('width', '5em');


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


/*** 
 *  Code to run on page load
***/

$(document).ready(function() {

    /* Add time picker to Time entry field */
    $(".time-entry").datetimepicker({
        timeOnly:true,
        buttonText: '<i class="fa fa-clock-o"></i>',
        format:'H:i'
    });

    /* Set width of Time entry field */
    $(".time-entry").css('width', '5em');

    /* Store dates for later use */
    start_date = getStartDate();
    end_date   = getEndDate();


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

    /**
     * Disable some of the forms for the UGA water history rows.
     */
    $(".UGA .uga-hide input").each(function() {
        $(this).prop('disabled', true);
    });

    $(".UGA .uga-time input").each(function() {
        $(this).datetimepicker('destroy');
    });

    // Initial settings for the number of rows to show
    $("#rows_option").html(showCompleteText);
    show15();
       	
    // Apply number of rows toggle to table
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

    // This will not work as long as the type in the input in 'number'

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
