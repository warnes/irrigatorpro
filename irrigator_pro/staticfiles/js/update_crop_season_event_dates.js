/**** Update crop events when season start date is changed ****/
function season_start_date_change() 
{
    $(this).css("background-color","#FFFF99");  /* Mark it for debugging */

    /* Date before any change */
    stored_date_str = this.stored_date
    stored_date_val = new Date( $.datepicker.parseDate( "yy-mm-dd", stored_date_str ) );

    /* Date after any change */
    this_date_str = this.value;
    this_date_val = new Date( $.datepicker.parseDate( "yy-mm-dd", this_date_str ) );

    /* Difference in Old and New Date  */
    var delta  = this_date_val - stored_date_val;

    /* Update season end date */
    season_end_date        = $("input#id_season_end_date");
    update_event_dates(season_end_date,         delta);

    /* Update crop event dates */
    cropseason_event_dates = $(".cropseason_field_wrapper .hasDatepicker");
    update_event_dates(cropseason_event_dates, delta);

}

/**** Update later dates when a crop event date is changed ****/
function crop_event_date_change() 
{
    /** Calculate change in date **/
    var this_row = $(this).parents("tr");

    /* Row input elements */
    var this_input = $(this_row).find("input[name$=event_date_before]");

    /* Dates for the current row */
    var this_date_str_before = this.stored_date;
    var this_date_str_after  = this.value;

    /* Stash the new date into the stored_date attribute */
    this_input.stored_date = this.value;

    $(this).css("background-color","#FFFF99");  /* Mark it for debugging */

    /* Convert date strings to date objects */
    var this_date_before = new Date( $.datepicker.parseDate( "yy-mm-dd", this_date_str_before ) );
    var this_date_after  = new Date( $.datepicker.parseDate( "yy-mm-dd", this_date_str_after  ) );

    /* Calculate change in dates */
    var delta  = this_date_after - this_date_before;

    /** Update following rows **/
    cropseason_event_dates =  $(this_row).nextAll("tr").find("input.hasDatepicker");
    update_event_dates(cropseason_event_dates, delta);
} 


/**** Utility function to update dates in passed list ****/ 
function update_event_dates(next_rows, delta)
{
    for(var i=0; i<next_rows.length; i++)
    {
        /* Row input element */
        var this_date_input  = next_rows[i];
        var this_date_str    = $(this_date_input).val();
        var this_date_obj    = new Date( $.datepicker.parseDate( "yy-mm-dd", this_date_str ) );

        /* Calculate new date */
        var new_date_obj = new Date(this_date_obj.valueOf() + parseInt(delta));
	
        /* Put the new value in place */
        var new_date_str = $.datepicker.formatDate("yy-mm-dd", new_date_obj);
        $(this_date_input).val(new_date_str );
        $(this_date_input).attr("stored_date", new_date_str );

	/* Mark it for debugging */
        $(this_date_input).css("background-color","#FFFFCC");   
    }
}





function set_event_range() {
    /*** 
         This function sets date ranges to the limits given 
         by season_start_date and season_end_date
    ***/ 

    /* Get the season start and end dates */
    minDate = $('input[id=id_season_start_date]').val();
    maxDate = $('input[id=id_season_end_date]').val();
    
    /* Restrict season end date to start after the season start date */
    $('input[id=id_season_end_date]').datepicker( 
        "option", "minDate", minDate
    )

    /* Restrict event dates to range specified by crop season */
    $('input[id$=date]').filter('[id^=id_cropseasonevent]').datepicker( 
        "option", "minDate", minDate
    ).datepicker(
        "option", "maxDate", maxDate
    );
} 


function show_non_key_events() {
    $('.non-key-event').toggleClass('hidden',false);
    $('.non-key-event').find('input[id$=date]').not('[type=hidden]').datepicker().css({'width':'7em', 'margin':'2px'});
}

 
function hide_non_key_events() {
    $('.non-key-event').toggleClass('hidden',true);
    $('.non-key-event').find('.hasDatepicker').datepicker('destroy');
}


$(function() {
    /* Update crop season event dates when crop season start date changes */
    $("#id_season_start_date").change( season_start_date_change );

    /* Update later dates when earlier dates change */
    $("div.cropseason_field_wrapper .hasDatepicker").change( crop_event_date_change );
    
    /* Set event date ranges on page load */ 
    set_event_range();
    
    $('input[id=id_season_start_date]').change(set_event_range);
    $('input[id=id_season_end_date]').change(set_event_range);
})
