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


$(document).ready(function() 
    {
        console.log("Will disable picker");
    	$('form input').each(function() {
            // Could be more refined and only destroy
            // on date fields, but there doesn't seem
            // to be an issue here.
            $(this).datepicker('destroy');
        }
       );
        
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



});
