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

    var select_1 = $('#'+select_div_id+' [name="region"]');
    if (select_1.val()!=""){
        var text1 = select_1.children('option[value="'+select_1.val()+'"]').text()
        span.append($("<a/>").attr("href", location_url+select_1.val()).text(text1));
    }

    var select_2 = $('#'+select_div_id+' [name="tik"]');
    if (select_2.val()!=""){
        var text2 = select_2.children('option[value="'+select_2.val()+'"]').text()
        span.append("&rarr;").append($("<a/>").attr("href", location_url+select_2.val()).text(text2));
    }

    var select_3 = $('#'+select_div_id+' [name="uik"]');
    if (select_3.val()!=""){
        var text3 = select_3.children('option[value="'+select_3.val()+'"]').text()
        span.append("&rarr;").append($("<a/>").attr("href", location_url+select_3.val()).text(text3));
    }
}

/* ---- Methods for manipulations with location selectors ---- */
// path is a list of region ids (top to bottom level) with length from 0 to 3
function set_select_location(div_id, path){
    var select_1 = $('#'+div_id+' [name="region"]');
    var select_2 = $('#'+div_id+' [name="tik"]');
    var select_3 = $('#'+div_id+' [name="uik"]');

    select_1.unbind().change(function(){
        select_3.hide();

        if (select_1.val()=="")
            select_2.val("").change();
        else
            $.getJSON(GET_SUB_REGIONS_URL, {location: select_1.val()}, function(data){
                if (data.length>0){
                    //select_2.children('[value!=""]').remove();
                    select_2.children().remove();

                    var empty_2 = $("<option/>").val("");
                    if (select_1.children('[value="'+select_1.val()+'"]').text()=="Зарубежные территории")
                        var txt = "Выберите страну";
                    else
                        var txt = "Выберите район";
                    select_2.append(empty_2.text(txt));

                    $.each(data, function(index, value){
                        select_2.append($("<option/>").val(value["id"]).text(value["name"]));
                    });
                    select_2.val(path.length>1 ? path[1] : "").change();
                }
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

    select_1.val(path.length>0 ? path[0] : select_1.val()).change();
    select_2.val(path.length>1 ? path[1] : "").change();
    select_3.val(path.length>2 ? path[2] : "");
}

function form_location_id(div_id){
    // This is a helper method to extract location id from selector block
    var select_1 = $('#'+div_id+' [name="region"]');
    var select_2 = $('#'+div_id+' [name="tik"]');
    var select_3 = $('#'+div_id+' [name="uik"]');

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
        //"click .icon":          "open"
    },

    initialize: function(li, username){
        this.el = li;
        this.username = (username!=undefined) ? username : $(this.el).children("a").text();

        this.attach_buttons();
    },

    attach_buttons: function(){
        var username = this.username;

        if ($(this.el).children("a").length==0)
            // TODO: explicit use of url (use global variable instead) - everywhere
            $("<a/>").attr("href", "/users/"+this.username+"/")
                    .text(this.username).appendTo($(this.el));

        if ($.inArray(username, CONTACTS)!=-1) //(USERNAME!="")
            var remove_btn = $("<span/>")
                    .attr("title", "Удалить из контактов")
                    .addClass("side_list_btn ui-icon ui-icon-close")
                    .tipsy({gravity: 'n'})
                    .click(function(){
                        remove_from_contacts_init(username);
                    })
                    .appendTo($(this.el));

        var report_btn = $("<span/>")
                .addClass("side_list_btn ui-icon ui-icon-notice")
                .appendTo($(this.el));
        if (username!=USERNAME && $.inArray(username, REPORTS["user"])==-1)
            report_btn.attr("title", "Пожаловаться на пользователя")
                    .tipsy({gravity: 'n'})
                    .click(function(){
                        if (USERNAME=="")
                            login_dialog_init("Чтобы пожаловаться на пользователя, пожалуйста, войдите в систему");
                        else
                            report_dialog_init("user", username);
                    });
        else
            report_btn.css("visibility", "hidden");

        if (username!=USERNAME && $.inArray(username, CONTACTS)==-1)
            var add_btn = $("<span/>")
                    .attr("title", "Добавить в контакты")
                    .addClass("side_list_btn ui-icon ui-icon-plus")
                    .tipsy({gravity: 'n'})
                    .click(function(){
                        if (USERNAME=="")
                            login_dialog_init("Чтобы добавить пользователя в контакты, пожалуйста, войдите в систему");
                        else
                            add_to_contacts_dialog_init(username);
                    })
                    .appendTo($(this.el));
    },

    render: function(){
        $(this.el).html("");

        this.attach_buttons();
        return this;
    }

});


var LinkListItem = Backbone.View.extend({
    tagName: "li",

    initialize: function(li, username){
        this.el = li;
        this.username = (username!=undefined) ? username : $(this.el).children("a").text();

        this.attach_buttons();
    },

    attach_buttons: function(){
        var username = this.username;

        if ($(this.el).children("a").length==0)
            // TODO: explicit use of url (use global variable instead) - everywhere
            $("<a/>").attr("href", "/users/"+this.username+"/")
                    .text(this.username).appendTo($(this.el));

        if (this.show_remove_btn && USERNAME!="")
            var remove_btn = $("<span/>")
                    .attr("title", "Удалить из контактов")
                    .addClass("side_list_btn ui-icon ui-icon-close")
                    .tipsy({gravity: 'n'})
                    .click(function(){
                        remove_from_contacts_init(username);
                    })
                    .appendTo($(this.el));

        if (username!=USERNAME)
            var report_btn = $("<span/>")
                    .attr("title", "Пожаловаться на пользователя")
                    .addClass("side_list_btn ui-icon ui-icon-notice")
                    .tipsy({gravity: 'n'})
                    .click(function(){
                        if (USERNAME=="")
                            login_dialog_init("Чтобы пожаловаться на пользователя, пожалуйста, войдите в систему");
                        else
                            report_user_dialog_init(username);
                    })
                    .appendTo($(this.el));

        if (username!=USERNAME && $.inArray(username, CONTACTS)==-1)
            var add_btn = $("<span/>")
                    .attr("title", "Добавить в контакты")
                    .addClass("side_list_btn ui-icon ui-icon-plus")
                    .tipsy({gravity: 'n'})
                    .click(function(){
                        if (USERNAME=="")
                            login_dialog_init("Чтобы добавить пользователя в контакты, пожалуйста, войдите в систему");
                        else
                            add_to_contacts_dialog_init(username);
                    })
                    .appendTo($(this.el));
    },

    render: function(){
        $(this.el).html("");

        this.attach_buttons();
        return this;
    }

});

// Return if a given user is in contacts of the current user
function in_contacts(username){
    var index = $.inArray(username, CONTACTS);
    return index!=-1;
}
