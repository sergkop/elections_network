$(document).ready(function(){

});

/* ---- Methods for manipulations with location path ---- */
// Get location path from html created inside element with span_id
function get_path(span_id){
    var path = [];
    $("#"+span_id+" a").each(function(index){
        var url_parts = $(this).attr("href").split("/");
        path.push(parseInt(url_parts[url_parts.length-1]));
    });
    return path;
}

// Update location path inside element with span_id using form data
function update_path(span_id, select_div_id){
    var location_url = "/location/"; // TODO: take it from django urls
    var span = $("#"+span_id)
    span.html("");

    var select_1 = $('#'+select_div_id+' [name="region_1"]');
    var text1 = select_1.children('option[value="'+select_1.val()+'"]').text()
    span.append($("<a/>").attr("href", location_url+select_1.val()).text(text1));

    var select_2 = $('#'+select_div_id+' [name="region_2"]');
    var text2 = select_2.children('option[value="'+select_2.val()+'"]').text()
    if (select_2.val()!="")
        span.append("&rarr;").append($("<a/>").attr("href", location_url+select_2.val()).text(text2));

    var select_3 = $('#'+select_div_id+' [name="region_3"]');
    var text3 = select_3.children('option[value="'+select_3.val()+'"]').text()
    if (select_3.val()!="")
        span.append("&rarr;").append($("<a/>").attr("href", location_url+select_3.val()).text(text3));
}

function login_dialog_buttons(dialog_id, login_url, intro_text){
    $("#"+dialog_id).dialog("option", "buttons", {
        "Войти": function(){window.location.href=login_url+"?next="+window.location.href;},
        "Отмена": function(){$("#"+dialog_id).dialog("close");}
    });
    $("#login_intro_span").text(intro_text);
}
