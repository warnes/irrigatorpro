$(function() {
    $('#formset tbody tr').formset({
        addText: '<i class="iTooltip add-icon fa fa-plus-square" help="Add Row"> Add Row</i>',
        deleteText: '<i class="iTooltip delete-icon fa fa-minus-square" help="Delete Row"></i>' //'Delete Row',
    })});



/**
 * Handles deletion of authorized user. Note that the next two methods are
 * used for authorized and invited users, where the user_type parameter will
 * specify the type of user. Should rename them, here and in html file.
 *
 *
 * @param user_info  used to recreate the row id (until I learn to do more complex
 *   operations in the template language. 
 *
 * @param pk the primary key for the user, used in hidden input.
 *
 */


function delete_auth_row(user_info, pk, user_type) {
    var rowID = createValidID(user_info);
    var hidden_input_id = "deleted_auth_" + user_type + "_" + pk; 
    $("#" + rowID).css("text-decoration", "line-through");

    var newCellContents = 
	"<button type='button' onclick='undo_auth_delete(\"" 
	+ rowID 
	+ "\", \""
	+ hidden_input_id 
	+ "\",\""
	+ pk
	+ "\",\""
	+ user_type
	+ "\")'>Undo</button>";

    $("#" + rowID + " td:nth-child(2)").html(newCellContents);

    $("#main-form").append(
	$('<input/>')
	    .attr('type', 'hidden')
	    .attr('name', 'deleted_user_' + user_type)
	    .attr('id', hidden_input_id)
	    .val(pk)
    );
}



/**
 * Undo the deletion of an authorized user.
 *
 * @param row_id the id of the row.
 * @param hidden_id the id of the hidden input.
 *
 */

function undo_auth_delete(row_id, hidden_id, pk, user_type) {

    $("#" + row_id).css("text-decoration", "");
    var newCellContents = 
	"<button type='button' onclick='delete_auth_row(\"" 
	+ row_id
	+ "\", \""
	+ pk
	+ "\",\""
	+ user_type
	+ "\")'>Delete</button>";


    $("#" + row_id + " td:nth-child(2)").html(newCellContents);
    $("#" + hidden_id).remove();
}




/**
 * Add an authorized row. In this case only an email is displayed.
 *
 * TODO Validate that we are not adding an existing row.
 */

function add_auth_row() {

    var newEmail = $("#new_auth_user").val();
    $("#new_auth_user").val("");
    var newID = "new_" + createValidID(newEmail);
    var myRow = "<tr id='" + newID +"'><td>" + newEmail 
	+ "</td><td><button type='button' onclick='delete_new_auth_row(\""
	+ newID
	+ "\")'>Delete</button></td></tr>";

    
    console.log("new row: " + myRow);
    $("#auth-users-body").append(myRow);


    $("#main-form").append(
	$('<input id="' + create_hidden_id(newEmail) + '"/>')
	    .attr('type', 'hidden')
	    .attr('name', 'added_user')
	    .val(newEmail)
    );
}


function delete_new_auth_row(id) {
    console.log("will remove row: " + id);
    $("#" + id).remove();

}


function create_hidden_id(id_or_email) {
    return "hidden_" + createValidID(id_or_email);
}
