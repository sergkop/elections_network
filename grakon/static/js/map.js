/**
 * Класс для избирательных округов
 * 
 * @param {level}
 *            уровень избирательного округа (от 1 до 3)
 * @param {data}
 *            объект типа {numVoters: 4, numObservers: 6}
 */
var ElectionCommission = function(id, level, shortTitle, title, address, xCoord, yCoord, data) {
	this.id = id;
	this.level = level < 1 ? 1 : level > 3 ? 3 : level;
	this.shortTitle = shortTitle;
	this.title = title;
	this.address = address;
	this.data = data;
	this.xCoord = xCoord;
	this.yCoord = yCoord;
};

var Grakon = {
	/**
	 * Три стиля (начальный, мышь на элементе и элемент выбран) для субъектов РФ
	 */
	REGION_STYLES: {
		'default':	new OpenLayers.Style({
					  'fillColor': '#66cccc',
					  'fillOpacity': 0.1,
					  'strokeColor': '#66cccc',
					  'strokeOpacity': 0.25,
					  'strokeWidth': 1
					}),
		'temporary':	new OpenLayers.Style({
						  'fillColor': '#ee9900',
						  'fillOpacity': 0.4,
						  'strokeColor': '#ee9900',
						  'strokeOpacity': 1,
						  'strokeWidth': 2,
						  'cursor': 'pointer'
						}),
		'select':	new OpenLayers.Style({
					  'fillColor': '#0000ff',
					  'fillOpacity': 0.4,
					  'strokeColor': '#0000ff',
					  'strokeOpacity': 1,
					  'strokeWidth': 2
					})
	},
	
	/**
	 * Три стиля (начальный, мышь на элементе и элемент выбран) для районов субъекта РФ
	 */
	DISTRICT_STYLES: {
		'default':	new OpenLayers.Style({
					  'fillColor': '#66cccc',
					  'fillOpacity': 0.2,
					  'strokeColor': '#000000',
					  'strokeOpacity': 0.75,
					  'strokeWidth': 2,
					  'strokeDashstyle': 'dot'
					}),
		'temporary':	new OpenLayers.Style({
						  'fillColor': '#ee9900',
						  'fillOpacity': 0.4,
						  'strokeColor': '#ee9900',
						  'strokeOpacity': 1,
						  'strokeWidth': 2,
						  'cursor': 'pointer'
						}),
		'select':	new OpenLayers.Style({
					  'fillColor': '#0000ff',
					  'fillOpacity': 0.4,
					  'strokeColor': '#0000ff',
					  'strokeOpacity': 1,
					  'strokeWidth': 2
					})
	},
	
	/**
	 * @private
	 * Объект OpenLayers.Map — используемая карта.
	 */
	map: null,
	
	/**
	 * Свойства создаваемой карты.
	 */
	MAP_OPTIONS: {
		projection: new OpenLayers.Projection("EPSG:900913"),
		units: "m",
		numZoomLevels: 18,
		displayProjection: new OpenLayers.Projection("EPSG:4326"),
		maxResolution: 156543.0339,
		maxExtent: new OpenLayers.Bounds(-20037508, -20037508, 20037508, 20037508.34),
		controls:[]
	},
	
	MAP_URLS: {
		regions: "/static/oblasts_simplified.json",
		electionCommissionsType2: "/static/election_commissions_level_2.txt",
		electionCommissionsType3: "/static/election_commissions_level_3.txt"
	},
	
	/**
	 * Уровень масштабирования карты, с которого показываются ТИКи.
	 */
	MAP_LEVELS_ZOOM: new Object({
		'country': 0,
		'regions': 3,
		'districts': 7,
		'areas': 11
	}),
	
	/**
	 * Массивы слоёв, соответсвующие уровню в иерархии избирательной комиссии
	 */
	borderLayers: new Object({
		'country': null,
		'regions': null,
		'districts': null,
		'areas': null
	}),
	
	electionCommissionLayers: new Object({
		'country': null,
		'regions': null,
		'districts': null,
		'areas': null
	}),
	
	electionCommissions: new Object(),

	/**
	 * Пространство имён для вспомогательных функций
	 */
	Utils: {			
		/**
		 * Обработчик клика по субъекту РФ. Максимално приближает карту к выбранному субъекту РФ.
		 * @param {feature} [OpenLayers.Feature] выбранный объект на карте
		 */
		regionClickHandler: function(feature) {
			if (feature != null && feature.geometry != null) {
				Grakon.map.zoomToExtent( feature.geometry.getBounds() );
				Grakon.map.zoomIn();
				Grakon.MAP_LEVELS_ZOOM.districts = Grakon.map.getZoom();
			}
		},
		
		districtClickHandler: function(feature) {
			if (feature != null && feature.geometry != null) {
				Grakon.map.zoomToExtent( feature.geometry.getBounds() );
				Grakon.map.zoomIn();
				Grakon.MAP_LEVELS_ZOOM.areas = Grakon.map.getZoom();
			}
		},
		
		/**
		 * callback-метод, который считывает данные из GeoJSON,
		 * возвращаемого в виде результата асинхронного запроса и
		 * добавляет их на слой субъектов РФ
		 * @private
		 * @param {request} указатель на объект асинхронного запроса
		 */
		addRegionBorders: function(request) {
			if (request.status == 200) {
				var geoJSON = new OpenLayers.Format.GeoJSON({
					'internalProjection': new OpenLayers.Projection("EPSG:900913"),
					'externalProjection': new OpenLayers.Projection("EPSG:4326")
				});
				var features = geoJSON.read(request.responseText);
				Grakon.borderLayers.regions.addFeatures(features);
			} else
				OpenLayers.Console.error("Запрос границ субъектов РФ из файла GeoJSON вернул статус: " + request.status);
		},
		
		addDistrictBorders: function(request) {
			if (request.status == 200) {
				var geoJSON = new OpenLayers.Format.GeoJSON({
					'internalProjection': new OpenLayers.Projection("EPSG:900913"),
					'externalProjection': new OpenLayers.Projection("EPSG:4326")
				});
				var features = geoJSON.read(request.responseText);
				Grakon.borderLayers.districts.addFeatures(features);
			} else
				OpenLayers.Console.error("Запрос границ районов субъекта РФ из файла GeoJSON вернул статус: " + request.status);
		}
	},
	
	/**
	 * Создаёт карту и слои с данными в HTML-контейнере с заданным ID.
	 * @param {mapDivID} ID HTML-контейнера [String]
	 */
	init: function(place) {
		var mapDivID = "publicElectionsMap";
		Grakon.setupLogging();
		Grakon.initMap(mapDivID);
		Grakon.initMapLayers();
		Grakon.initMapTools();
		
		Grakon.setUserLocation();
		Grakon.setDefaultView(place);
	},
	
	/**
     * Отмечает приблизительное местоположение пользователя на карте
     */
    setUserLocation: function() {
        // Определяем координаты пользователя и отмечаем на карте
        if (YMaps.location) {
            var size = new OpenLayers.Size(32,32);
			var offset = new OpenLayers.Pixel(-(size.w/2), -(size.h/2));
			var icon = new OpenLayers.Icon('/static/images/user.png', size, offset);
			var userCoords = new OpenLayers.LonLat(YMaps.location.longitude,YMaps.location.latitude).transform(new OpenLayers.Projection("EPSG:4326"), Grakon.map.getProjectionObject());
			var user = new OpenLayers.Marker(userCoords,icon);
			var infoLayer = new OpenLayers.Layer.Markers("Users", {projection: new OpenLayers.Projection("EPSG:4326")});
			infoLayer.addMarker(user);
			Grakon.map.addLayer(infoLayer);
        }
    },
	
	/**
     * Центрирует карту на указанном месте с оптимальным масштабом.
     * 
     * @param {place} -
     *            место, которое будет показано на карте. Если не задано, то
     *            будет показана вся Россия
     */
    setDefaultView: function(place) {
        var zoom = Grakon.MAP_LEVELS_ZOOM.regions+1;
        var center = new OpenLayers.LonLat(47.57138, 54.8384).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));

        // Показываем заданное место на карте.
        if (place == null || place == "") { // Если место не задано, то для
                                            // пользователя из России будет
                                            // определено его местоположение и
                                            // показано на карте с максимальным
                                            // масштабом;
            // для пользователя из-за рубежа карта будет отцентрована по
            // европейской части России.
            if (YMaps.location && YMaps.location.country == "Россия") {
                center = new OpenLayers.LonLat(YMaps.location.longitude, YMaps.location.latitude).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
                zoom = YMaps.location.zoom;
            }

            Grakon.map.setCenter(center, zoom);
        } else {
            var geocoder = new YMaps.Geocoder(place, {
                geocodeProvider : "yandex#map"
            });
            // Создает обработчик успешного завершения геокодирования
            YMaps.Events.observe(geocoder, geocoder.Events.Load, function() {
                // Если объект найден, устанавливает центр карты в центр области
                // показа объекта
                    if (this.length()) {
                        var left = this.get(0).getBounds().getLeft();
						var bottom = this.get(0).getBounds().getBottom();
						var right = this.get(0).getBounds().getRight();
						var top = this.get(0).getBounds().getTop();
						var bounds = new OpenLayers.Bounds(left, bottom, right, top).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
						Grakon.map.zoomToExtent(bounds);
                    } else
                        Grakon.map.setCenter(center, zoom);
			});

            // Процесс геокодирования завершен с ошибкой
            YMaps.Events.observe(geocoder, geocoder.Events.Fault, function(gc, error) {
                OpenLayers.Console.error("Произошла ошибка: " + error);
            });
        }
    },
	
	/**
	 * Задаёт способ вывода логов и сообщений об ошибках
	 */
	setupLogging: function() {
		OpenLayers.Console = window.console;
		OpenLayers.Console.userError = OpenLayers.Console.error;
	},
	
	/**
	 * Создаёт карту в заданном HTML-контейнере
	 * @param {mapDivID} ID HTML-контейнера [String]
	 */
	initMap: function(mapDivID) {
		Grakon.map = new OpenLayers.Map(mapDivID, Grakon.MAP_OPTIONS);
		
		// слушаем событие окончания масштабирования
		Grakon.map.events.register("zoomend", Grakon.map, function() {
			// границы регионов
			if (Grakon.borderLayers.regions != null)
				Grakon.borderLayers.regions.setVisibility( this.getZoom() < Grakon.MAP_LEVELS_ZOOM.districts );
			
			// границы районов
			if (Grakon.borderLayers.districts != null)
				Grakon.borderLayers.districts.setVisibility( this.getZoom() >= Grakon.MAP_LEVELS_ZOOM.districts );
				
			// видимость ИКСов
			if (Grakon.electionCommissionLayers.regions != null)
				Grakon.electionCommissionLayers.regions.setVisibility( this.getZoom() >= Grakon.MAP_LEVELS_ZOOM.regions );
				
			// видимость ТИКов
			if (Grakon.electionCommissionLayers.districts != null)
				Grakon.electionCommissionLayers.districts.setVisibility( this.getZoom() >= Grakon.MAP_LEVELS_ZOOM.districts );
				
			// видимость УИКов
			if (Grakon.electionCommissionLayers.areas != null)
				Grakon.electionCommissionLayers.areas.setVisibility( this.getZoom() >= Grakon.MAP_LEVELS_ZOOM.areas );
		});
		
		// слушаем событие окончания перемещения по карте
		Grakon.map.events.register("moveend", Grakon.map, function() {
			if (Grakon.map.getZoom() >= Grakon.MAP_LEVELS_ZOOM.areas) {
				var bounds = Grakon.map.getExtent().transform(Grakon.map.getProjectionObject(), new OpenLayers.Projection("EPSG:4326")).toArray();
				var left = bounds[0];
				var bottom = bounds[1];
				var right = bounds[2];
				var top = bounds[3];
				OpenLayers.loadURL("/location/locations_data",
					{'x1': left,
					'x2': right,
					'y1': bottom,
					'y2': top},
					null,
					function(request) {
						if (request.status == 200) {
							eval(request.responseText);
							if (electionCommissions != null) {
								// Добавим слой УИКи
								if (Grakon.electionCommissionLayers.areas == null) {
									var areasLayer = new OpenLayers.Layer.Markers( "УИКи" );
									Grakon.electionCommissionLayers.areas = areasLayer;
									Grakon.map.addLayer( areasLayer );
								}
								
								// Добавим новые (не показанные) УИКи на карту
								for (var uikID in electionCommissions)
									if (Grakon.electionCommissions[uikID] == null) {
										Grakon.electionCommissions[uikID] = electionCommissions[uikID];
										var size = new OpenLayers.Size(18,32);
										var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
										var icon = new OpenLayers.Icon('/static/images/uik.png', size, offset);
										var uikLocation = new OpenLayers.LonLat(electionCommissions[uikID].xCoord,electionCommissions[uikID].yCoord).transform(new OpenLayers.Projection("EPSG:4326"), Grakon.map.getProjectionObject());
										var uik = new OpenLayers.Marker(uikLocation,icon);
										uik.data = electionCommissions[uikID];
										var popup = new OpenLayers.Popup.AnchoredBubble(uik.data.id, uikLocation,
																	 new OpenLayers.Size(300,200),
																	 uik.data.address,
																	 icon, true, null);
										Grakon.map.addPopup(popup);
										popup.hide();
										Grakon.map.events.register('click', uikLocation, function(){popup.show();});
										Grakon.electionCommissionLayers.areas.addMarker(uik);
									}
							}
						} else
							OpenLayers.Console.error("Запрос избирательных комиссий для заданного квадрата вернул статус: " + request.status);
					},
					function() {
						OpenLayers.Console.error("Ошибка при загрузке избирательных комиссий для заданного квадрата.");
					}
				);
			}
		});
	},
	
	/**
	 * Создаёт и добавляет слои на карту
	 */
	initMapLayers: function() {
		var Y_map = new OpenLayers.Layer.Yandex("Карта-схема от Яндекс",{sphericalMercator: true});
		var Y_sat = new OpenLayers.Layer.Yandex("Вид со спутника от Яндекс",{type:YMaps.MapType.SATELLITE, sphericalMercator:true});
		var Y_hyb = new OpenLayers.Layer.Yandex("Гибридный вид от Яндекс",{type:YMaps.MapType.HYBRID, sphericalMercator:true});
		var OSM_map = new OpenLayers.Layer.OSM("Карта-схема от OpenStreetMap");
		Grakon.map.addLayer(Y_map);
		Grakon.map.addLayer(OSM_map);
		Grakon.map.addLayer(Y_sat);
		Grakon.map.addLayer(Y_hyb);
		Grakon.map.setBaseLayer(Y_hyb);
		
		Grakon.addRegions();
		Grakon.addDistricts();
		Grakon.addElectionCommissions();
	},
	
	/**
	 * Создать векторный слой субъектов РФ с выделением цветом при действиях мыши и добавить его на карту
	 */
	addRegions: function() {			
		var regions = new OpenLayers.Layer.Vector("Субъекты РФ", {
			projection: new OpenLayers.Projection("EPSG:4326"),
			styleMap: new OpenLayers.StyleMap(Grakon.REGION_STYLES)
		});

		// выделять субъект РФ цветом при наведении мыши
		var highlightCtrl = new OpenLayers.Control.SelectFeature(regions, {
			hover: true,
			highlightOnly: true,
			renderIntent: "temporary"
		});
		Grakon.map.addControl(highlightCtrl);
		highlightCtrl.activate();

		// показать субъект РФ на всю карту при клике на нём
		var selectCtrl = new OpenLayers.Control.SelectFeature(regions, {
			clickout: true,
			select: Grakon.Utils.regionClickHandler
		});
		Grakon.map.addControl(selectCtrl);
		selectCtrl.activate();

		// Добавить слой на карту
		Grakon.map.addLayer(regions);
		Grakon.borderLayers.regions = regions;

		// Загрузить данные на слой
		OpenLayers.loadURL(Grakon.MAP_URLS.regions, {}, Grakon.Utils, Grakon.Utils.addRegionBorders, function() {
			OpenLayers.Console.error("Ошибка при загрузке границ субъектов РФ");
		});
	},
	
	/**
	 * Создать векторный слой субъектов РФ с выделением цветом при действиях мыши и добавить его на карту
	 */
	addElectionCommissions: function() {
		// Добавляем слой ТИКов
		var electionCommissionsLevel3 = new OpenLayers.Layer.Text("ТИКи", {
			location: Grakon.MAP_URLS.electionCommissionsType3,
			projection: new OpenLayers.Projection("EPSG:4326")
		});
		electionCommissionsLevel3.setVisibility(false);
		Grakon.map.addLayer(electionCommissionsLevel3);
		Grakon.electionCommissionLayers.districts = electionCommissionsLevel3;
		
		// Добавляем слой ИКСов
		var electionCommissionsLevel2 = new OpenLayers.Layer.Text("ИКСы", {
			location: Grakon.MAP_URLS.electionCommissionsType2,
			projection: new OpenLayers.Projection("EPSG:4326")
		});
		Grakon.map.addLayer(electionCommissionsLevel2);
		Grakon.electionCommissionLayers.regions = electionCommissionsLevel2;
	},
	
	addDistricts: function() {			
		var districts = new OpenLayers.Layer.Vector("Районы", {
			projection: new OpenLayers.Projection("EPSG:4326"),
			styleMap: new OpenLayers.StyleMap(Grakon.DISTRICT_STYLES)
		});
		// Добавить слой на карту
		districts.setVisibility(false);
		Grakon.borderLayers.districts = districts;
		
		// выделять субъект РФ цветом при наведении мыши
		var highlightCtrl = new OpenLayers.Control.SelectFeature(districts, {
			hover: true,
			highlightOnly: true,
			renderIntent: "temporary"
		});
		Grakon.map.addControl(highlightCtrl);
		highlightCtrl.activate();

		// показать субъект РФ на всю карту при клике на нём
		var selectCtrl = new OpenLayers.Control.SelectFeature(districts, {
			clickout: true,
			select: Grakon.Utils.districtClickHandler
		});
		Grakon.map.addControl(selectCtrl);
		selectCtrl.activate();
		
		Grakon.map.addLayer(districts);
	},
	
	/**
	 * Добавляет инструменты управления на карту (например, масштабирование и выбор слоя)
	 */
	initMapTools: function() {
		Grakon.map.addControl(new OpenLayers.Control.PanZoomBar());                  		
		Grakon.map.addControl(new OpenLayers.Control.LayerSwitcher());
		Grakon.map.addControl(new OpenLayers.Control.Navigation());
		Grakon.map.addControl(new OpenLayers.Control.MousePosition());
	}
};
