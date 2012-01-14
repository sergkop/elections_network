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
                $("#links_ul").append($("<li/>").append(
                    $("<a/>").attr("target", "_blank").attr("href", $("#link_url_input").val()).text($("#link_name_input").val())
                ));
            $("#add_link_dialog").dialog("destroy");
        });
    });

    // TODO: dialogs don't open the second time
    // Report link dialog
    $("#report_link").button();
    $("#report_link_dialog").dialog({width:650, height:250, modal: true});
    $("#report_link_dialog").dialog("close");
    $("#report_link").click(function(){
        $("#report_link_dialog").dialog("open");
        $("#report_link_ul li").remove();
        console.log($("#links_ul"));
        $("#links_ul li").each(function(index){
            var url = $(this).children("a").attr("href");
            var text = $(this).text();
            var a_copy = $("<a/>").attr("href", url).text(text);
            var radio_btn = $("<input/>").attr("type", "radio").attr("name", "report_link_radio").attr("value", url);
            $("#report_link_ul").append($("<li/>").append(radio_btn).append(a_copy));
        });
    });
    $("#report_link_submit").click(function(){
        $.post($("#report_link_form").attr("action"), $("#report_link_form").serialize(), function(data){
            console.log(data);
            $("#report_link_dialog").dialog("destroy");
            alert("Ваша жалоба будет рассмотрена в ближайшее время");
        });
    });

    // Register as a voter dialog
    $("#become_voter_dialog").dialog({width:650, height:250, modal: true});
    $("#become_voter_dialog").dialog("close");
    $("#become_voter").button();
    $("#become_voter").click(function(){
        $("#become_voter_dialog").dialog("open");
    });
    $("#select_region_1").val(current_location);
    $("#become_voter_submit").click(function(){
        $.post($("#become_voter_form").attr("action"), $("#become_voter_form").serialize(), function(data){
            $("#become_voter_dialog").dialog("destroy");
        });
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

    //-----------Main page code-----------------
    $("#goto_region").button();
    //$("#goto_region2").button();
    $("#goto_region").click(function() {
        location.href="/location/"+$("#select_region_1").val();
    });
    /*$("#goto_region2").click(function() {
        location.href="location_uik.html";
    });*/

    //------------Profile page-----------------
    $("#send_message").button();
    $("#add_to_contacts").button();
    $("#report_user").button();
});
