/**** Update crop events when season start date is changed ****/
function season_start_date_change() 
{
    $(this).css("background-color", "red");
    this_date_str = this.value;
    this_date_val = new Date( $.datepicker.parseDate( "yy-mm-dd", this_date_str ) );
    console.log("this_date_str=" + this_date_str);
    console.log("this_date_val=" + this_date_val);

    cropSeasonEvent_datepicker_list = $("input[name$=date]").filter("[name^=cropseasonevent]").filter(".hasDatepicker");
    for(var i=0; i < 2 /*cropSeasonEvent_datepicker_list.length*/; i++)
    { 
        console.log("i=" + i );								

        /* Date input fields */								 
        cropSeasonEvent_date_visible_input = cropSeasonEvent_datepicker_list[i]
        cropSeasonEvent_date_hidden_input  = $(cropSeasonEvent_datepicker_list[i]).parents("tr").find("input[name$=event_date_before]");

        if(undefined == cropSeasonEvent_date_visible_input) break;

        console.log("cropSeasonEvent_date_visible_input=" + cropSeasonEvent_date_visible_input);
        console.log("cropSeasonEvent_date_hidden_input=" + cropSeasonEvent_date_hidden_input);

        /* Date values */
        cropSeasonEvent_date_str   = cropSeasonEvent_date_visible_input.value;
	cropSeasonEvent_date_val   = new Date( $.datepicker.parseDate( "yy-mm-dd", cropSeasonEvent_date_str ) );

        console.log("this_date_str=" + cropSeasonEvent_date_str);
        console.log("this_date_val=" + cropSeasonEvent_date_val);

	if( cropSeasonEvent_date_val < this_date_val) 
        {
            var newdate=$.datepicker.formatDate("yy-mm-dd", this_date_val);
	    $(cropSeasonEvent_date_hidden_input ).attr("value", newdate );
	    $(cropSeasonEvent_date_visible_input).attr("value", newdate );

	    $(cropSeasonEvent_date_hidden_input ).value = newdate;
	    $(cropSeasonEvent_date_visible_input).value = newdate;

            $(cropSeasonEvent_date_visible_input).css("background-color","pink");

            /*** THIS LINE ISN'T WORKING PROPERLY ****/
            $(cropSeasonEvent_date_visible_input).change();

            /*$(cropSeasonEvent_date_visible_input).css("background-color","pink");*/
        }
    }
}

/**** Update later dates when a crop event date is changed ****/
function crop_event_date_change() 
{
    /** Calculate change in date **/
    var this_row = $(this).parents("tr");
    console.log(this_row);               

    /* Row input elements */
    var this_input_before = $(this_row).find("input[name$=event_date_before]");
    var this_input_after  = this;

    /* Dates for the current row */
    var this_date_str_before = this_input_before.attr("value");
    var this_date_str_after  = this.value;

    /* Stash the new date into the hidden 'before' input */
    this_input_before.attr("value",this.value);

    $(this).css("background-color","lightyellow");  /* Mark it for debugging */

    /* Convert date strings to date objects */
    var this_date_before = new Date( $.datepicker.parseDate( "yy-mm-dd", this_date_str_before ) );
    var this_date_after  = new Date( $.datepicker.parseDate( "yy-mm-dd", this_date_str_after  ) );

    /* Calculate change in dates */
    var delta  = this_date_after - this_date_before;

    /** Update following rows **/
    next_rows = $(this_row).nextAll("tr")

    for(var i=0; i<next_rows.length; i++)
    {
        var next_row = next_rows[i];

        /* Row input elements */
        var next_date_before_input = $(next_row).find("input[name=event_date_before]");
        var next_date_after_input  = $(next_row).find(".hasDatepicker");
        
        /* Dates for the current row */
        var next_date_str_before = $(next_date_before_input).attr("value");
        var next_date_str_after  = $(next_date_after_input ).attr("value");
	
        /* Convert date strings to date objects */
        var next_date_before = new Date( $.datepicker.parseDate( "yy-mm-dd", next_date_str_before ) );

        /* Calculate new date */
        var next_date_after = new Date(next_date_before.valueOf() + parseInt(delta));
	
        /* Put the new value in place */
        var next_date_after_str = $.datepicker.formatDate("yy-mm-dd", next_date_after);
        $(next_date_before_input).attr("value", next_date_after_str );
        $(next_date_after_input ).attr("value", next_date_after_str );

        $(next_date_after_input).css("background-color","lightyellow");   /* Mark it for debugging */
    }

} 
