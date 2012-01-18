$(document).ready(function() {

    //assign button actions
    $("#become_observer").button();
    $("#find_my_uik").button();
    $("#login_dialog").dialog({width:300,height:150, modal: true}).dialog("close");
    $("#login").click(function() {
        $("#login_dialog").dialog("open");
    });

    $("#register").click(function() {
        $("#login_dialog").dialog("open");
    });
});
