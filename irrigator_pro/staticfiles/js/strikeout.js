/**
 * Mark row elements as strikethrough if checkbox is set 
**/
function rowStrikeOutCheckbox(flag)
{
    if( this.checked ) {
	$(this).closest('tr').find(':not([rowspan])').css('text-decoration','line-through')
    }
    else
    {
	$(this).closest('tr').find(':not([rowspan])').css('text-decoration','')
    }
}

$(document).ready(function() {
    // Make row elements 'strikethrough' if Ignore/Delete checked
    $(':checkbox').change( rowStrikeOutCheckbox ); // trigger
    $(':checkbox').each(rowStrikeOutCheckbox);         // initial
})