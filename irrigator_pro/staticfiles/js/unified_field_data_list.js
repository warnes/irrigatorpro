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

    /** PROBLEM HERE: getStartDate is defined in the HTML file **/
    start_date = getStartDate();
    end_date   = getEndDate();



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
     * Set the warnings for all the rows.
     */
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
    
    if( newDate < start_date || newDate > end_date )
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
