var Address = {
    VIB_ID: 100100031793505,
    AUTHENTICITY_TOKEN: "6c3e5ba2e795907e32ba0d4fb1e3b16a206bf074",
    VIB_TITLE: "Выборы Президента Российской Федерации 4 марта 2012 года",
    addressId: null,
    DEFAULT_MESSAGE: 'Выберите свой адрес',

    Utils: {
        pathParts: new Array(),
        titleParts: new Array(),
        levels: new Array(),

        addSelect: function(data) {
            var index = $('div#addressFields > select').length;
            var level = new Object();

            $('div#addressFields').append( $('<select/>').attr('id', index) );
            // TODO: change default message depending on the level
            $('select#'+index).append( $('<option/>').attr('selected', 'selected').text(Address.DEFAULT_MESSAGE) );
            $.each(data, function(key, value){
                var id = value.attr.id;
                $('select#'+index).append( $('<option/>').attr('value', id).text( value.attr.caption ) );
                level[id] = value;
            });

            Address.Utils.levels.push(level);

            $('select#'+index).change(function() {
                var id = $(this).children('option:selected').val();
                $("div#result").html("");
                if (id!="") {
                    $(this).nextAll('select').remove();
                    var index = $(this).prevAll('select').length;
                    for (var i=Address.Utils.levels.length-1; i>index; i--) {
                        Address.Utils.pathParts.pop();
                        Address.Utils.titleParts.pop();
                        Address.Utils.levels.pop();
                    }
                    Address.addressId = Address.Utils.levels[index][id].attr.addrId;
                    Address.Utils.pathParts[index] = id;
                    Address.Utils.titleParts[index] = Address.Utils.levels[index][id].attr.caption;
                    Address.showLevelById(id, index+1);
                }
            });
        },

        getAddressPath: function() {
            return Address.Utils.pathParts.join(", ");
        },

        getAddressTitle: function() {
            return Address.Utils.titleParts.join(", ");
        }
    },

    showLevelById: function(id, level) {
        $.ajax({
            url: '/uik_search_data',
            data: {
                url: 'gettreelevel',
                'id': id,
                'level': level
            },
            dataType: 'json',
            success: function(response) {
                if (response.length > 0)
                    Address.Utils.addSelect(response);
                else
                    Address.findUIK();
            },
            error: function() {
                alert("Извините! Произошла какая-то ошибка. Попробуйте ещё раз.");
            }
        });
    },

    findUIK: function() {
        $.ajax({
            url: '/uik_search_data',
            data: {
                url: 'showresult', 
                authenticityToken: Address.AUTHENTICITY_TOKEN,
                sendRequest: encodeURIComponent('Отправить запрос'),
                addressId: Address.addressId,
                vibId: Address.VIB_ID,
                subjfed: "",
                subjfedName: "",
                addressTitle: encodeURIComponent(Address.Utils.getAddressTitle()),
                vibTitle: encodeURIComponent(Address.VIB_TITLE),
                addressPath: Address.Utils.getAddressPath()
            },
            dataType: 'html',
            success: function(html) {
                if ($(html).find("div.dotted").length > 0)
                    $('#result').show().text( $(html).find("div.dotted").text() );
                else if ($(html).attr("id") == "uik")
                    $('#result').show().text( $(html).text() );
                else {
                    $('#result').html( "Уважаемый пользователь! К сожалению, данные не были найдены." );
                }
            },
            alert: function() {
                alert('Извините! Запрос не сработал. Попробуйте ещё раз.');
            }
        });
    }
}

$(document).ready(function(){
    $('#addressFields').html("");
    $('#result').html("");
    Address.showLevelById("path_", 0);
});
