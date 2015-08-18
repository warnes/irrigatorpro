var labelCell     = 1;
var farmCell     = 2;
//var commTypeCell = 4;
var alertLevelCell = 4;
var notificationTime_col = 5;
var timezone_col = 6;


function editRow(notifications_pk) {
    
    $("#notifications_table button").each(
        function() {
            $(this)[0].disabled = true;
        }
    );
    
    $("#new_row_pk").val(notifications_pk)
    $("#edit-entry").css("visibility", "visible");

    var tableRow = document.getElementById("row_"+notifications_pk);
    
    $("#edit-label")[0].value = tableRow.cells[labelCell].innerHTML.trim();

    // First get the right selected farm
    var pk = $('#row_' + notifications_pk + ' .farm-cell').attr('data-pk');
    //$("#select-farm .farm-option").removeAttr("selected");
    $(".farm-option[data-pk=" + pk + "]").each(function() {
        $("#select-farm").val($(this).val());
    });

    update_selection_lists();

    // Set selected fields.
    $("#row_" + notifications_pk + " .current-field").each(function() {
        $(".field-option[data-pk=" + $(this).attr("data-pk") + "]").attr("selected", "selected");
    });

    // Set selected users
    $("#row_" + notifications_pk + " .current-user").each(function() {
        $(".user-option[data-pk=" + $(this).attr("data-pk") + "]").attr("selected", "selected");
    });

    $("#edit_row_alert_level_" + createValidID(tableRow.cells[alertLevelCell].innerHTML.trim()))[0].selected = true;
    //$("#edit_row_comm_type_" + tableRow.cells[commTypeCell].innerHTML.trim())[0].selected = true;
    $("#edit_row_nt_" + createValidID(tableRow.cells[notificationTime_col].innerHTML.trim()))[0].selected = true;
    $("#edit_row_tz_" + createValidID(tableRow.cells[timezone_col].innerHTML.trim()))[0].selected = true;
}




function addRow() {
    
    $("#notifications_table button").each(
        function() {
            $(this)[0].disabled = true;
        }
    );

    // Clear all previous input. In
    $("#edit-entry input").not("#save-new").not("[type='hidden']").val('');


    $("#edit-entry").css("visibility", "visible");
    $("#select-farm")[0].selectedIndex = 0;
    $("#select-farm").change();
    
    // Use default selection for time zone, notification time
    $("#edit_row_tz_US_Eastern")[0].selected = true;
    $("#edit_row_nt_5_00_am")[0].selected = true;
}

function validate_form(myform) {
    var returnedValue = true;
    $("#field-needed").css("display", "none");
    $("#recipient-needed").css("display", "none");
    $("#label-needed").css("display", "none");
    
    if (document.getElementById("select-fields").selectedIndex < 0) {
        $("#field-needed").css("display", "");
        returnedValue = false;
    }
    if (document.getElementById("select-users").selectedIndex < 0) {
        $("#recipient-needed").css("display", "");
        returnedValue = false;
    }
    
    if (document.getElementById("edit-label").value.trim() == "") {
        $("#label-needed").css("display", "");
        returnedValue = false;
    }
    
    // Check that the label is not null
    
    
    if (returnedValue == false){
        return false;
    }
    window.onbeforeunload = null;
    myform.submit();    
}


$(document).ready(function() {
    /**
     * Called when the selected farm has changed. Must update the list
     * of fields and users.
     */
    
    $('#select-farm').change(function() {
        update_selection_lists();
    });

    $("#cancelEdit").click(function(){
        if (confirm("Are you sure you want to stop? Any change will be lost")) {
            window.onbeforeunload = null;
            $("#edit-entry").css("visibility", "hidden");
            //$("#edit-row")[0].reset();
            $("#notifications_table button").each(            
                function() {
                    $(this)[0].disabled = false;
                }
            );
        }
    });



    //$('select').chosen();    	
    //$('.chosen-container').css('width','auto');

});    
