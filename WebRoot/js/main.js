$(document).ready(function() {
   //assign button actions
	$("#become_observer").button();
	$("#become_voter").button();
	$("#find_my_uik").button();
	$("#login2").button();
    $("#login_dialog").dialog({width:300,height:150, modal: true});
	$("#login_dialog").dialog("close");
	$("#login").click(function() {
		//show login dialog
		$("#login_dialog").dialog("open");
	});
	
	$("#login2").click(function() {
		//show login dialog
		$("#login_dialog").dialog("open");
	});
	$("#register").click(function() {
		//show login dialog
		$("#login_dialog").dialog("open");
	});
	$("#goto_region").button();
	$("#goto_region2").button();
	$("#goto_region").click(function() {
		location.href="location_uik.html";
	});
	$("#goto_region2").click(function() {
		location.href="location_uik.html";
	});
 });