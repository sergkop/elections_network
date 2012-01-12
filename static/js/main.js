$(document).ready(function() {
    // Add links dialog
    $("#add_link_dialog").dialog({width:650, height:250, modal: true});
    $("#add_link_dialog").dialog("close");
    $("#add_link").button();
    $("#add_link").click(function(){
        $("#add_link_dialog").dialog("open");
    });
    $("#add_link_submit").button();
    $("#add_link_submit").click(function(){
        $.post($("#add_link_form").attr("action"), $("#add_link_form").serialize(), function(data){
            if (data=="ok")
                $("#links_list").append($("<li/>").append(
                    $("<a/>").attr("target", "_blank").attr("href", $("#link_url_input").val()).text($("#link_name_input").val())
                ));
            $("#add_link_dialog").dialog("destroy");
        });
    });

    // Register as a voter dialog
    $("#become_voter_dialog").dialog({width:650, height:250, modal: true});
    $("#become_voter_dialog").dialog("close");
    $("#become_voter").button();
    $("#become_voter").click(function(){
        $("#become_voter_dialog").dialog("open");
    });

    //assign button actions
    $("#become_observer").button();
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
        location.href=$("#select_region").val();
    });
    $("#goto_region2").click(function() {
        location.href="location_uik.html";
    });
});
