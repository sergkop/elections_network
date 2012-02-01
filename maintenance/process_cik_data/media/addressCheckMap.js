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
		
		// Показать на карте заданное место
		AddressCheckMap.setDefaultViewport(place);
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
		
		if (!document.getElementById('all').checked)
			AddressCheckMap.type = document.getElementById('house').checked ? "house" :
                    document.getElementById('street').checked ? "street" :
                    document.getElementById('locality').checked ? "district" :
                    document.getElementById('locality').checked ? "locality" :
                    document.getElementById('province').checked ? "province" : null;

		AddressCheckMap.map.removeOverlay( AddressCheckMap.geoResult );
		$("#message").html("");
		$("#error").html("");
		
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
    },

	getCoordinates: function(addressString) {
		// Запускает асинхронный поиск адреса
		var geocoder = new YMaps.Geocoder(addressString, {geocodeProvider: "yandex#pmap", boundedBy: AddressCheckMap.map.getBounds(), strictBounds: true});
		
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
						
			if (AddressCheckMap.geoResult == null && addressParts.length > 1) {
				var geocoder2 = new YMaps.Geocoder(addressString, {geocodeProvider: "yandex#map", boundedBy: AddressCheckMap.map.getBounds(), strictBounds: true});
				YMaps.Events.observe(geocoder, geocoder.Events.Load, function (geocoder) {
					AddressCheckMap.geoResult = null;

					for (var i=0; i < this.length() && AddressCheckMap.geoResult == null; i++)
						for (var j=0; j < AddressCheckMap.searchTypes.length && AddressCheckMap.geoResult == null; j++)
							if (this.get(i).kind == AddressCheckMap.searchTypes[j])
								//if (this.get(i).kind != "house" || addressString.match(/(\d+)/ig) != null)
									if (AddressCheckMap.type == null || AddressCheckMap.type == this.get(i).kind)
										AddressCheckMap.geoResult = this.get(i);
								
					if (AddressCheckMap.geoResult == null) {
						addressParts.pop(); // remove the last element from the array
                        AddressCheckMap.getCoordinates(addressParts.join(" "));
					} else if (AddressCheckMap.geoResult != null) {
						AddressCheckMap.map.setBounds( AddressCheckMap.geoResult.getBounds() );
						AddressCheckMap.map.addOverlay( AddressCheckMap.geoResult );

                        AddressCheckMap.formData(addressString);
					}
				});
				
				YMaps.Events.observe(geocoder, geocoder.Events.Fault, function (geocoder) {
					alert("Произошла ошибка при запросе! Повторите запрос снова!");
				});
				
			} else if (AddressCheckMap.geoResult != null) {
				AddressCheckMap.map.setBounds( AddressCheckMap.geoResult.getBounds() );
				AddressCheckMap.map.addOverlay( AddressCheckMap.geoResult );

                AddressCheckMap.formData(addressString);
			} else {
				var geocoder2 = new YMaps.Geocoder(addressString, {geocodeProvider: "yandex#map", boundedBy: AddressCheckMap.map.getBounds(), strictBounds: true});
				YMaps.Events.observe(geocoder, geocoder.Events.Load, function (geocoder) {
					AddressCheckMap.geoResult = null;

					for (var i=0; i < this.length() && AddressCheckMap.geoResult == null; i++)
						for (var j=0; j < AddressCheckMap.searchTypes.length && AddressCheckMap.geoResult == null; j++)
							if (this.get(i).kind == AddressCheckMap.searchTypes[j])
								//if (this.get(i).kind != "house" || addressString.match(/(\d+)/ig) != null)
									if (AddressCheckMap.type == null || AddressCheckMap.type == this.get(i).kind)
										AddressCheckMap.geoResult = this.get(i);
								
					if (AddressCheckMap.geoResult != null) {
						AddressCheckMap.map.setBounds( AddressCheckMap.geoResult.getBounds() );
						AddressCheckMap.map.addOverlay( AddressCheckMap.geoResult );
						
						AddressCheckMap.formData(addressString);
					} else {
						AddressCheckMap.map.setZoom(3);
						$("#error").text("Адрес на найден!");
					}
				});
				
				YMaps.Events.observe(geocoder, geocoder.Events.Fault, function (geocoder) {
					alert("Произошла ошибка при запросе! Повторите запрос снова!");
				});
			}
		});
		
		YMaps.Events.observe(geocoder, geocoder.Events.Fault, function (geocoder) {
			AddressCheckMap.map.setZoom(3);
			$("#error").text("Адрес на найден!");
		});
	}
};