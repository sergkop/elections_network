$(document).ready(function() {

    //assign button actions
    $("#become_observer").button();
    $("#find_my_uik").button();
    $("#login2").button();
    $("#login_dialog").dialog({width:300,height:150, modal: true}).dialog("close");
    $("#login").click(function() {
        $("#login_dialog").dialog("open");
    });

    $("#login2").click(function() {
        $("#login_dialog").dialog("open");
    });
    $("#register").click(function() {
        $("#login_dialog").dialog("open");
    });

    //-----------Main page code-----------------
    $("#goto_region").button().click(function() {
        location.href="/location/"+$("#select_region_1").val();
    });
});
