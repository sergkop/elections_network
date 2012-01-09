$(document).ready(function() {
   //assign button actions
	$("#become_observer").button();
	$("#become_voter").button();
	$("#find_my_uik").button();
	$("#login_dialog").dialog({width:300,height:150});
	$("#login_dialog").dialog("close");
	$("#uik_search_dialog").dialog({width:650, height:250});
	$("#uik_search_dialog").dialog("close");
	$("#login").click(function() {
		//show login dialog
		$("#login_dialog").dialog("open");
	});
	$("#register").click(function() {
		//show login dialog
		$("#login_dialog").dialog("open");
	});
	$("#find_my_uik").click(function() {$("#uik_search_dialog").dialog("open");});
	$("#find_my_ui_link").click(function() {$("#uik_search_dialog").dialog("open");});
	$("#find_uik_button").button();
	$("#goto_region").button();
 });