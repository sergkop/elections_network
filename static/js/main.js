$(document).ready(function(){

});

// Default tipsy settings
$.fn.tipsy.defaults.delayIn = 300;
$.fn.tipsy.defaults.delayOut = 300;
$.fn.tipsy.defaults.fade = true;
$.fn.tipsy.defaults.opacity = 0.6;

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
    if (select_1.val()!=""){
        var text1 = select_1.children('option[value="'+select_1.val()+'"]').text()
        span.append($("<a/>").attr("href", location_url+select_1.val()).text(text1));
    }

    var select_2 = $('#'+select_div_id+' [name="region_2"]');
    if (select_2.val()!=""){
        var text2 = select_2.children('option[value="'+select_2.val()+'"]').text()
        span.append("&rarr;").append($("<a/>").attr("href", location_url+select_2.val()).text(text2));
    }

    var select_3 = $('#'+select_div_id+' [name="region_3"]');
    if (select_3.val()!=""){
        var text3 = select_3.children('option[value="'+select_3.val()+'"]').text()
        span.append("&rarr;").append($("<a/>").attr("href", location_url+select_3.val()).text(text3));
    }
}

/* ---- Methods for manipulations with location selectors ---- */
// path is a list of region ids (top to bottom level) with length from 0 to 3
    function set_select_location(div_id, path){
        var select_1 = $('#'+div_id+' [name="region_1"]');
        var select_2 = $('#'+div_id+' [name="region_2"]');
        var select_3 = $('#'+div_id+' [name="region_3"]');

        select_1.unbind().change(function(){
            select_3.hide();

            if (select_1.val()==""){
                select_2.hide();
                select_2.val("").change();
            }
            else
                $.getJSON(GET_SUB_REGIONS_URL, {location: select_1.val()}, function(data){
                    if (data.length>0){
                        select_2.show();
                        select_2.children('[value!=""]').remove();
                        $.each(data, function(index, value){
                            select_2.append($("<option/>").val(value["id"]).text(value["name"]));
                        });
                        select_2.val(path.length>1 ? path[1] : "").change();
                    } else
                        select_2.hide();
                });
        });

        select_2.unbind().change(function(){
            if (select_2.val()=="")
                select_3.hide();
            else {
                $.getJSON(GET_SUB_REGIONS_URL, {location: select_2.val()}, function(data){
                    if (data.length>0){
                        select_3.show();
                        select_3.children('[value!=""]').remove();
                        $.each(data, function(index, value){
                            select_3.append($("<option/>").val(value["id"]).text(value["name"]));
                        });
                        select_3.val(path.length>2 ? path[2] : "");
                    } else
                        select_3.hide();
                });
            }
        });

        select_1.val(path.length>0 ? path[0] : "").change();
        select_2.val(path.length>1 ? path[1] : "").change();
        select_3.val(path.length>2 ? path[2] : "");
    }

function form_location_id(div_id){
    // This is a helper method to extract location id from selector block
    var select_1 = $('#'+div_id+' [name="region_1"]');
    var select_2 = $('#'+div_id+' [name="region_2"]');
    var select_3 = $('#'+div_id+' [name="region_3"]');

    if (select_3.val()!="")
        return select_3.val();
    if (select_2.val()!="")
        return select_2.val();
    if (select_1.val()!="")
        return select_1.val();

    return "";
}

/*-----------------------------------------  */

var UserListItem = Backbone.View.extend({
    tagName: "li",

    //className: "document-row",

    events: {
        //"click .icon":          "open",
        //"click .button.edit":   "openEditDialog",
        //"click .button.delete": "destroy"
    },

    // show_remove_btn is boolean showing if remove button should be added
    initialize: function(username, show_remove_btn){
        // TODO: explicit use of url (use global variable instead)
        $(this.el).html("");

        var link = $("<a/>").attr("href", "/users/"+username).text(username);
        $(this.el).append(link);

        if (show_remove_btn){
            var remove_btn = $("<span/>").attr("title", "Удалить из контактов")
                    .addClass("side_list_btn ui-icon ui-icon-close").tipsy({gravity: 'n'});
            $(this.el).append(remove_btn);
        }

        var report_btn = $("<span/>")
                .attr("title", "Пожаловаться на пользователя")
                .addClass("side_list_btn ui-icon ui-icon-notice")
                .tipsy({gravity: 'n'})
                .click(function(){
                    if (USERNAME=="")
                        login_dialog_buttons("report_user_dialog", LOGIN_URL,
                                "Чтобы пожаловаться на пользователя, пожалуйста, войдите в систему");
                    else
                        $("#report_user_hidden_username").val(username);
                    $("#report_user_dialog").dialog("open");
                })
                .appendTo($(this.el));

        if (username!=USERNAME && !(username in CONTACTS)){
            var add_btn = $("<span/>")
                    .attr("title", "Добавить в контакты")
                    .addClass("side_list_btn ui-icon ui-icon-plus")
                    .tipsy({gravity: 'n'})
                    .click(function(){
                        if (USERNAME=="")
                            login_dialog_buttons("report_user_dialog", LOGIN_URL,
                                    "Чтобы пожаловаться на пользователя, пожалуйста, войдите в систему");
                        else
                            $("#report_user_hidden_username").val(username);
                        $("#report_user_dialog").dialog("open");
                    })
                    .appendTo($(this.el));
        }
    },

    render: function() {}
});



function add_user_list_buttons(li){
    var username = li.children("a").text();

    
    user_li_report_btn.click(function(){
        alert("report");
    });
    user_li_remove_btn.click(function(){
        alert("report");
    });
    
    $(this).append(user_li_report_btn).append(user_li_remove_btn);
    
    if (USERNAME==""){
        
    } else {
        
    }
}
