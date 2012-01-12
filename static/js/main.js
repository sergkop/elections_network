$(document).ready(function() {
    // Add links dialog
    $("#add_link_dialog").dialog({width:650, height:250, modal: true});
    $("#add_link_dialog").dialog("close");
    $("#add_link").click(function(){
        $("#add_link_dialog").dialog("open");
    });
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
    $("#register_as_izbr_dialog").dialog({width:650, height:250, modal: true});
    $("#register_as_izbr_dialog").dialog("close");
    $("#register_as_izbr").click(function(){
        $("#register_as_izbr_dialog").dialog("open");
    });
});
