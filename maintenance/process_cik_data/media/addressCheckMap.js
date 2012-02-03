var AddressCheckMap = {
    map: null,
    
    geoResult: null,
    
    searchTypes: new Array("country", "province", "locality", "district", "street", "house"),
    
    type: null,
    
    /**
     * Добавляем Народную Яндекс.Карту на страницу
     */
    init: function(place) {
        AddressCheckMap.map = new YMaps.Map( document.getElementById("map") );
        AddressCheckMap.map.setType(YMaps.MapType.PHYBRID);
        AddressCheckMap.map.enableScrollZoom();
    
        // Переименовываем типы карт, чтобы их можно было различать. Народные карты имеют индекс 1, обычные - индекс 2.
        YMaps.MapType.PMAP.setName("Схема 1");
        YMaps.MapType.MAP.setName("Схема 2");
        YMaps.MapType.PHYBRID.setName("Гибрид 1");
        YMaps.MapType.HYBRID.setName("Гибрид 2");
        AddressCheckMap.map.addControl(new YMaps.TypeControl([YMaps.MapType.PMAP, YMaps.MapType.MAP, YMaps.MapType.SATELLITE, YMaps.MapType.PHYBRID, YMaps.MapType.HYBRID,], [0,1,2,3,4])); // объявляем доступные типы карт
        AddressCheckMap.map.addControl(new YMaps.Zoom());
        AddressCheckMap.map.addControl( new YMaps.SearchControl({geocodeOptions: {geocodeProvider: "yandex#map"}, width: 295}) );
        AddressCheckMap.map.addControl( new YMaps.SearchControl({geocodeOptions: {geocodeProvider: "yandex#pmap"}, width: 295}), new YMaps.ControlPosition(YMaps.ControlPosition.TOP_LEFT, new YMaps.Point(5, 5)) );
        
        YMaps.Events.observe(AddressCheckMap.map, AddressCheckMap.map.Events.Click, function (map, clickEvent) {
            map.removeOverlay( AddressCheckMap.geoResult );
            AddressCheckMap.setPlacemark( clickEvent.getGeoPoint(), $('#map_address').val() );
        });
        
        // Показать на карте заданное место
        AddressCheckMap.setDefaultViewport(place);
    },
    
    setPlacemark: function(geoPoint, addressString) {
        // Запускает процесс геокодирования
        var geocoder = new YMaps.Geocoder(geoPoint);
        
        AddressCheckMap.geoResult = new YMaps.Placemark(geoPoint);
        AddressCheckMap.geoResult.description = "(" + AddressCheckMap.geoResult.getCoordPoint().getX() + ", " + AddressCheckMap.geoResult.getCoordPoint().getY() + ")";
        
        // Обработчик успешного завершения процесса геокодирования
        YMaps.Events.observe(geocoder, geocoder.Events.Load, function () {
            for (var i=0; i<this.length(); i++)
                AddressCheckMap.geoResult.description += "<p>"+this.get(i).text+"</p>";

            AddressCheckMap.map.addOverlay( AddressCheckMap.geoResult );
            
            AddressCheckMap.formData(addressString);
        });
         
        // Обработчик неудачного завершения геокодирования
        YMaps.Events.observe(geocoder, geocoder.Events.Fault, function (geocoder, error) {
            AddressCheckMap.map.addOverlay( AddressCheckMap.geoResult );
            
            AddressCheckMap.formData(addressString);
        });
    },
    
    /**
     * Центрирует карту на указанном месте с оптимальным масштабом.
     * @param {place} - место, которое будет показано на карте. Если не задано, то будет показана вся Россия
     */
    setDefaultViewport: function(place) {
        if (place == null || place == "") { // Если место не задано место, то будет показана вся Россия
            var zoom = 3;
            var center = new YMaps.GeoPoint(95, 65);
            AddressCheckMap.map.setCenter(center, zoom);
        } else
            // если место задано, то оно будет показано на карте
            AddressCheckMap.showAddress(place, false);
    },
    
    /**
     * Функция для отображения результата геокодирования на карте.
     * @param {value} - адрес объекта для поиска
     * @param {peoplesMap} - [boolean] true, поиск по Народной Карте Яндекс; false, поиск по обычной Карте Яндекс
     */
    showAddress: function(value, peoplesMap) {
        // Запускает процесс геокодирования
        var geocodeProviderValue = peoplesMap ? "yandex#pmap" : "yandex#map";
        var geocoder = new YMaps.Geocoder(value, {geocodeProvider: geocodeProviderValue});

        // Создает обработчик успешного завершения геокодирования
        YMaps.Events.observe(geocoder, geocoder.Events.Load, function () {
            // Если объект найден, устанавливает центр карты в центр области показа объекта
            if (this.length())
                AddressCheckMap.map.setBounds(this.get(0).getBounds());
            else
                alert("Ничего не найдено. Извините, пожалуйста!");
        });

        // Процесс геокодирования завершен с ошибкой
        YMaps.Events.observe(geocoder, geocoder.Events.Fault, function (gc, error) {
            alert("Произошла ошибка: " + error);
        });
    },

    showCoordinates: function() {
        var region = $("#region").text();
        var addressString = document.getElementById('map_address').value;
        AddressCheckMap.type = null;

        AddressCheckMap.map.removeOverlay( AddressCheckMap.geoResult );

        if (region.length > 0) {
            var geocoder = new YMaps.Geocoder(region, {geocodeProvider: "yandex#map"});
            YMaps.Events.observe(geocoder, geocoder.Events.Load, function () {
                if (this.length()) {
                    AddressCheckMap.map.setBounds(this.get(0).getBounds());

                    AddressCheckMap.getCoordinates( addressString );
                } else
                    alert("Область не найдена. Извините, пожалуйста!");
            });

            // Процесс геокодирования завершен с ошибкой
            YMaps.Events.observe(geocoder, geocoder.Events.Fault, function (gc, error) {
                alert("Произошла ошибка: " + error);
            });
        } else
            AddressCheckMap.getCoordinates( addressString );
            
        return false;
    },

    formData: function(addressString){
        $("#map_address").val(addressString);
        $("#x_coord").val(AddressCheckMap.geoResult.getCoordPoint().getX());
        $("#y_coord").val(AddressCheckMap.geoResult.getCoordPoint().getY());
        $("#add_geo").attr("checked", "checked");
    },

    getCoordinates: function(addressString) {
        // Запускает асинхронный поиск адреса
        var geocoder = new YMaps.Geocoder(addressString, {geocodeProvider: "yandex#map", boundedBy: AddressCheckMap.map.getBounds(), strictBounds: true});
        
        // Объявляем callback-функцию для поиска адреса
        YMaps.Events.observe(geocoder, geocoder.Events.Load, function (geocoder) {
            var addressParts = addressString.split(" ");
            AddressCheckMap.geoResult = null;

            for (var i=0; i < this.length() && AddressCheckMap.geoResult == null; i++)
                for (var j=0; j < AddressCheckMap.searchTypes.length && AddressCheckMap.geoResult == null; j++)
                    if (this.get(i).kind == AddressCheckMap.searchTypes[j])
                        //if (this.get(i).kind != "house" || addressString.match(/(\d+)/ig) != null)
                            if (AddressCheckMap.type == null || AddressCheckMap.type == this.get(i).kind)
                                AddressCheckMap.geoResult = this.get(i);

            if (AddressCheckMap.geoResult != null) {
                AddressCheckMap.map.setBounds( AddressCheckMap.geoResult.getBounds() );
                AddressCheckMap.setPlacemark( AddressCheckMap.geoResult.getGeoPoint(), addressString );
            }
        });
        
        YMaps.Events.observe(geocoder, geocoder.Events.Fault, function (geocoder) {
            AddressCheckMap.map.setZoom(3);
        });
    }
};