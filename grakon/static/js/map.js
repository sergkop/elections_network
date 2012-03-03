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
    this.level = level < 1 ? 1 : level > 4 ? 4 : level;
    this.shortTitle = shortTitle;
    this.title = title;
    this.address = address;
    this.data = data;
    this.xCoord = xCoord;
    this.yCoord = yCoord;
};



/**
 * Класс всплывающих окон. Используется при плике на метке карты.
 */
var AnchoredPopup = OpenLayers.Class(OpenLayers.Popup.Anchored, {
    'minSize': new OpenLayers.Size(256, 64)
});



/**
 * Класс с функциями для обработки событий с кнопками статистики
 */
var StatisticsButtonHandlers = new Object({
    activate: function(event) {
        // деактивируем другие кнопки панели
        var statisticBtnsPanel = Grakon.map.getControlsBy("displayClass", "olControlPanel").pop();
        for (var pos in statisticBtnsPanel.controls)
            if (statisticBtnsPanel.controls[pos].displayClass != event.object.displayClass)
                statisticBtnsPanel.controls[pos].deactivate();
            
        Grakon.selectedStatistics = event.object.displayClass;

        Grakon.electionCommissionLayers.regions.clearMarkers();
        Grakon.electionCommissionLayers.districts.clearMarkers();
        Grakon.electionCommissionLayers.areas.clearMarkers();
        Grakon.electionCommissions = new Array();
        $(".markerLabel").remove();
        
        Grakon.loadLocationsData();
    },
    deactivate: function(event) {
        Grakon.electionCommissionLayers.regions.clearMarkers();
        Grakon.electionCommissionLayers.districts.clearMarkers();
        Grakon.electionCommissionLayers.areas.clearMarkers();
        Grakon.electionCommissions = new Array();
        $(".markerLabel").remove();
        
        Grakon.selectedStatistics = null;
        
        Grakon.loadLocationsData();
    }
});



var Grakon = {
    /**
     * Три стиля (начальный, мышь на элементе и элемент выбран) для субъектов РФ
     */
    REGION_STYLES: {
        'default':  new OpenLayers.Style({
                      'fillColor': '#66cccc',
                      'fillOpacity': 0.1,
                      'strokeColor': '#66cccc',
                      'strokeOpacity': 0.25,
                      'strokeWidth': 1
                    }),
        'temporary':    new OpenLayers.Style({
                          'fillColor': '#ee9900',
                          'fillOpacity': 0.4,
                          'strokeColor': '#ee9900',
                          'strokeOpacity': 1,
                          'strokeWidth': 2,
                          'cursor': 'pointer'
                        }),
        'select':   new OpenLayers.Style({
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
        'default':  new OpenLayers.Style({
                      'fillColor': '#66cccc',
                      'fillOpacity': 0.2,
                      'strokeColor': '#000000',
                      'strokeOpacity': 0.75,
                      'strokeWidth': 2,
                      'strokeDashstyle': 'dot'
                    }),
        'temporary':    new OpenLayers.Style({
                          'fillColor': '#ee9900',
                          'fillOpacity': 0.4,
                          'strokeColor': '#ee9900',
                          'strokeOpacity': 1,
                          'strokeWidth': 2,
                          'cursor': 'pointer'
                        }),
        'select':   new OpenLayers.Style({
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
    
    layerSwitcher: null,
    
    /**
     * Свойства создаваемой карты.
     */
    MAP_OPTIONS: {
        projection: new OpenLayers.Projection("EPSG:3857"),
        displayProjection: new OpenLayers.Projection("EPSG:4326"),
        maxExtent: new OpenLayers.Bounds(-180, -85.051, 180, 85.051).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:3857")),
        maxResolution: 156543.0339,
        units: "m",
        controls: new Array()
    },
    
    MAP_URLS: {
        regions: "/static/oblasts_simplified.json"
    },
    
    ELECTION_COMMISSION_IMAGES: {
        "default": {
            2: "/static/images/iks.png",
            3: "/static/images/tik.png",
            4: "/static/images/uik.png"
        },
        "label": {
            2: "/static/images/iksNums.png",
            3: "/static/images/tikNums.png",
            4: "/static/images/uikNums.png"
        }
    },
    
    /**
     * Уровень масштабирования карты, с которого показываются ТИКи.
     */
    MAP_LEVELS_ZOOM: new Object({
        'country': 0,
        'regions': 3,
        'districts': 7,
        'areas': 11,
        'max': 16
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
    
    selectedStatistics: null,

    /**
     * Пространство имён для вспомогательных функций
     */
    Utils: {        
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
                    'internalProjection': new OpenLayers.Projection("EPSG:3857"),
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
                    'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                    'externalProjection': new OpenLayers.Projection("EPSG:4326")
                });
                var features = geoJSON.read(request.responseText);
                Grakon.borderLayers.districts.addFeatures(features);
            } else
                OpenLayers.Console.error("Запрос границ районов субъекта РФ из файла GeoJSON вернул статус: " + request.status);
        },
        
        /**
         * Показываем избирательные округа на карте
         * @private
         * @param {request} Объект XMLHttpRequest с результатами в виде массива JS из объектов ElectionCommission.
         */
        visualizeElectionCommissions: function(request) {
            if (request.status == 200) {
                if (request.responseText.indexOf('electionCommissions') == -1)
                    return;
                eval(request.responseText);
                if (electionCommissions) {
                    // Добавим новые (не показанные) избирательные комиссии на карту
                    for (var id in electionCommissions)
                        if (Grakon.electionCommissions[id] == null) {
                            Grakon.electionCommissions[id] = id;
                            var location = new OpenLayers.LonLat(electionCommissions[id].xCoord,electionCommissions[id].yCoord).transform(new OpenLayers.Projection("EPSG:4326"), Grakon.map.getProjectionObject());
                            var popupContentHTML = Grakon.Utils.buildElectionCommissionMarkerContent(electionCommissions[id]);
                            Grakon.Utils.addMarker(id, electionCommissions[id].level, location, popupContentHTML, electionCommissions[id].data);
                        }
                }

                Grakon.Utils.removeOutOfMapBoundsMarkers( Grakon.electionCommissionLayers.regions );
                Grakon.Utils.removeOutOfMapBoundsMarkers( Grakon.electionCommissionLayers.districts );
                Grakon.Utils.removeOutOfMapBoundsMarkers( Grakon.electionCommissionLayers.areas );
                
                Grakon.Utils.hideCloseDistrictMarkers();

            } else
                OpenLayers.Console.error("Запрос избирательных комиссий для заданного квадрата вернул статус: " + request.status);
        },

        removeOutOfMapBoundsMarkers: function(layer) {
            for (var pos in layer.markers) {
                if (!Grakon.map.getExtent().containsLonLat( layer.markers[pos].lonlat )) {
                    Grakon.electionCommissions[ layer.markers[pos].ecID ] = null;
                    layer.markers[pos].destroy();
                    layer.removeMarker( layer.markers[pos] );
                }
            }
        },
        
        /**
         * Скрывает метки для ТИКов, которые расположены слишком близко к уже добавленным на карту.
         */
        hideCloseDistrictMarkers: function() {
            var visible = new Array();
            var tooClose;
            for (var i in Grakon.electionCommissionLayers.districts.markers) {
                
                var marker = Grakon.electionCommissionLayers.districts.markers[i];
                var markerPixel = Grakon.map.getPixelFromLonLat( marker.lonlat );
                
                tooClose = false;
                for (var j=0; j<visible.length && !tooClose; j++)
                    if (Grakon.Utils.squareDistance(markerPixel, visible[j]) <= 32*32)
                        tooClose = true;
                    
                marker.display(!tooClose);
                if (!tooClose)
                    visible.push(markerPixel);
            }
        },
        
        /**
         * @param {electionCommission} объект класса ElectionCommission
         * @returns строку HTML используемую в качестве контента для всплывающей подсказки на метке
         */
        buildElectionCommissionMarkerContent: function(electionCommission) {
            var type;
            switch(electionCommission.level) {
              case 1: type = 'Центральная Избирательная Комиссия'; break;
              case 2: type = 'Избирательная Комиссия Субъекта РФ'; break;
              case 3: type = 'Территориальная Избирательная Комиссия'; break;
              case 4: type = 'Участковая Избирательная Комиссия'; break;
            }
            var title = ((electionCommission.level == 4) ? "УИК №" : "") + electionCommission.title;
            
            var content = '<h3><a href="#" class="zoomIn" onclick="Grakon.zoomOnElectionCommission('+electionCommission.xCoord+', '+electionCommission.yCoord+', '+electionCommission.level+'); return false;">'+title+'</a></h3>';
            content += '<p class="commissionType">'+type+'</p>';
            content += '<p><a href="/location/'+electionCommission.id+'">Страница комиссии</a></p>';
            content += '<p class="address">'+electionCommission.address+'</p>';
            if (electionCommission.data != null) {
                content += "<p>";
                content += (electionCommission.data.voters != null) ? "Избирателей: " + electionCommission.data.voters + "<br/>" : "";
                content += (electionCommission.data.observers != null) ? "Наблюдателей: " + electionCommission.data.observers + "<br/>" : "";
                content += (electionCommission.data.members != null) ? "Членов комиссии: " + electionCommission.data.members + "<br/>" : "";
                content += (electionCommission.data.journalists != null) ? "Представителей СМИ: " + electionCommission.data.journalists + "<br/>" : "";
                content += (electionCommission.data.prosecutors != null) ? "Прокуроров: " + electionCommission.data.prosecutors + "<br/>" : "";
                content += (electionCommission.data.authorities != null) ? "Чиновников: " + electionCommission.data.authorities + "<br/>" : "";
                content += "</p>";
            }
            return content;
        },
        
        removePopups: function() {
            if (Grakon.map.popups != null) {
                for (var n in Grakon.map.popups) {
                    Grakon.map.popups[n].toggle();
                    Grakon.map.removePopup( Grakon.map.popups[n] );
                }
            }
        },
        
        /**
         */
        addMarker: function(ecID, level, location, content, data) {
            var markers;
            switch(level) {
                case 2: layer = Grakon.electionCommissionLayers.regions; break;
                case 3: layer = Grakon.electionCommissionLayers.districts; break;
                case 4: layer = Grakon.electionCommissionLayers.areas; break;
                default: return;
            }
            
            var iconMode = "default";
            var iconSize = new OpenLayers.Size(18, 32);
            var iconOffset = new OpenLayers.Pixel(-9, -32);
            var iconLabel = "";
            if (Grakon.selectedStatistics != null) {
                iconMode = "label";
                iconSize = new OpenLayers.Size(36, 45);
                iconOffset = new OpenLayers.Pixel(-18, -45);
                iconLabel = (data[Grakon.selectedStatistics] != null) ? data[Grakon.selectedStatistics] : 0;
            }
            var feature = new OpenLayers.Feature(layer, location); 
            feature.closeBox = true;
            feature.popupClass = AnchoredPopup;
            feature.data.popupContentHTML = content;
            feature.data.overflow = "auto";
            feature.data.icon = new OpenLayers.Icon(
                Grakon.ELECTION_COMMISSION_IMAGES[iconMode][level],
                iconSize,
                iconOffset);
                    
            var marker = new OpenLayers.Marker.LabelMarker(location, feature.data.icon, iconLabel);
            marker['ecID'] = ecID;
            marker['data'] = data;
 
            marker.events.register("mousedown", feature, Grakon.Utils.markerClick);
            marker.events.register("mouseover", feature, Grakon.Utils.markerHover);
            marker.events.register("mouseout", feature, Grakon.Utils.markerHover);
 
            layer.addMarker(marker);
        },
        
        markerClick: function (evt) {
            Grakon.Utils.removePopups();
            
            this.popup = this.createPopup(this.closeBox);
            Grakon.Utils.updateCommissionZoomIcon(this.popup);
            Grakon.map.addPopup(this.popup);
            
            OpenLayers.Event.stop(evt);
        },
        
        markerHover: function (evt) {
            if (Grakon.map.popups != null && Grakon.map.popups[0] != null && Grakon.map.popups[0].id != "hint")
                return;
            
            Grakon.Utils.removePopups();
            
            if (evt.type == "mouseover") {
                var pattern = /\<a[^\>]+\>([^\<]+)\<\/a\>\<\/h3\>/;
                var matches = pattern.exec(this.data.popupContentHTML);
                
                if (matches != null) {
                    var width = (matches[1].length + 5) * 10;
                    
                    var type = "";
                    if (this.data.icon.url.indexOf("iks") != -1)
                        type = "ИКС: ";
                    else if (this.data.icon.url.indexOf("tik") != -1)
                        type = "ТИК: ";
                    
                    var content = "<center><b>"+type+matches[1]+"</b></center>";
                    var popup = new OpenLayers.Popup.Anchored("hint", this.lonlat, new OpenLayers.Size(width, 28), content, null, false);
                    Grakon.map.addPopup(popup);
                }
                OpenLayers.Event.stop(evt);
            }
        },

        /**
         * @param {level} уровень приближения карты
         * @returns масштаб для заданного уровня приближения на карте
         */
        getZoomForLevel: function(level) {
            var zoom;
            switch (level) {
              case 2: zoom = Grakon.MAP_LEVELS_ZOOM.regions; break;
              case 3: zoom = Grakon.MAP_LEVELS_ZOOM.districts; break;
              case 4: zoom = Grakon.MAP_LEVELS_ZOOM.areas; break;
              default: zoom = 4;
            }
            return zoom;
        },
        
        /**
         * @param {level} уровень/тип комиссии
         * @returns масштаб для заданного уровня приближения на карте
         */
        getLayerForLevel: function(level) {
            var layer;
            switch (level) {
              case 2: layer = Grakon.electionCommissionLayers.regions; break;
              case 3: layer = Grakon.electionCommissionLayers.districts; break;
              case 4: layer = Grakon.electionCommissionLayers.areas; break;
              default: layer = null;
            }
            return layer;
        },
        
        /**
         * Обработчик события открытия попапа при клике на метку.
         * Меняет картинку лупы в зависимости от масштаба.
         * @param {popup} объект типа OpenLayers.Popup
         */
        updateCommissionZoomIcon: function(popup) {
            if (popup == null)
                return;
            var contentHTML = popup.contentHTML;
            if (Grakon.map.getZoom() >= Grakon.MAP_LEVELS_ZOOM.max)
                popup.setContentHTML( contentHTML.replace("zoomIn", "zoomOut") );
            else
                popup.setContentHTML( contentHTML.replace("zoomOut", "zoomIn") );
        },
        
        /**
         * Обаботчик события клика на регионе или районе.
         * Если объект умещается на карте, то масштабировать карту на нём,
         * иначе приблизить на один уровень к указанной позиции.
         * @param {feature} выбранный регион или район на карте.
         */
        clickRegionHandler: function(feature) {
            if (feature != null && feature.geometry != null &&
                Grakon.map.getZoom() < Grakon.map.getZoomForExtent( feature.geometry.getBounds() ))
                    Grakon.map.zoomToExtent( feature.geometry.getBounds() );
            else {
                var mousePositionCtrl = Grakon.map.getControlsByClass("OpenLayers.Control.MousePosition")[0];
                var center = Grakon.map.getLonLatFromPixel( mousePositionCtrl.lastXy );
                var zoom = Grakon.map.getZoom() + 1;
                Grakon.map.setCenter(center, zoom);
            }
        },
        
        /**
         * Подсчитывает квадрат расстояния между двумя пикселями
         * @param {pixel1} первый пиксель OpenLayers.Pixel
         * @param {pixel2 второй пиксель OpenLayers.Pixel
         * @returns возвращает квадрат расстояния как float
         */
        squareDistance: function(pixel1, pixel2) {
            return (pixel1.x - pixel2.x) * (pixel1.x - pixel2.x) + (pixel1.y - pixel2.y) * (pixel1.y - pixel2.y);
        },
        
        /**
         * Calculates the pixels per unit for a given unit.
         * @param lonlat a point
         * @param uom the unit
         * @returns {Number} pixels per unit
         */
        calculatePixelsPerUnit: function(lonlat, uom) {
            var geometryCenterPixel = Grakon.map.getPixelFromLonLat(lonlat);
            var pixelSizeInKm = Grakon.map.getGeodesicPixelSize(geometryCenterPixel);
            
            var metersPerPixel = Math.max(pixelSizeInKm.w, pixelSizeInKm.h) * 1000;
            return OpenLayers.INCHES_PER_UNIT[uom] * OpenLayers.METERS_PER_INCH / metersPerPixel;
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
            var size = new OpenLayers.Size(24,24);
            var offset = new OpenLayers.Pixel(-(size.w/2), -(size.h/2));
            var icon = new OpenLayers.Icon('/static/images/user.png', size, offset);
            var userCoords = new OpenLayers.LonLat(YMaps.location.longitude,YMaps.location.latitude).transform(new OpenLayers.Projection("EPSG:4326"), Grakon.map.getProjectionObject());
            var user = new OpenLayers.Marker(userCoords,icon);
            var infoLayer = new OpenLayers.Layer.Markers("Ваше местоположение", {projection: new OpenLayers.Projection("EPSG:4326")});
            infoLayer.displayInLayerSwitcher = false;
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
        var center = new OpenLayers.LonLat(47.57138, 54.8384).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:3857"));

        // Показываем заданное место на карте.
        if (place == null || place == "") { // Если место не задано, то для
                                            // пользователя из России будет
                                            // определено его местоположение и
                                            // показано на карте с максимальным
                                            // масштабом;
            // для пользователя из-за рубежа карта будет отцентрована по
            // европейской части России.
            if (YMaps.location && YMaps.location.country == "Россия") {
                center = new OpenLayers.LonLat(YMaps.location.longitude, YMaps.location.latitude).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:3857"));
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
                        var bounds = new OpenLayers.Bounds(left, bottom, right, top).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:3857"));
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
		if (OpenLayers.Console != null)
			OpenLayers.Console.userError = OpenLayers.Console.error;
		else {
			OpenLayers.Console = new Object({
				log: function(msg) {},
				debug: function(msg) {alert(msg);},
				info: function(msg) {},
				warn: function(msg) {},
				userError: function(msg) {},
				error: function(msg) {}
			});
		}
    },
    
    /**
     * Создаёт карту в заданном HTML-контейнере
     * @param {mapDivID} ID HTML-контейнера [String]
     */
    initMap: function(mapDivID) {
        Grakon.map = new OpenLayers.Map(mapDivID, Grakon.MAP_OPTIONS);
        
        // слушаем событие окончания масштабирования
        Grakon.map.events.register("zoomend", Grakon.map, Grakon.mapZoomEndHandler);
        
        // слушаем событие окончания перемещения по карте
        Grakon.map.events.register("moveend", Grakon.map, Grakon.loadLocationsData);
    },
    
    /**
     * Формирует запрос и скачивает данные об избирательных участках для видимой области на карте
     */
    loadLocationsData: function() {
        var bounds = Grakon.map.getExtent().transform(Grakon.map.getProjectionObject(), new OpenLayers.Projection("EPSG:4326")).toArray();
        var left = bounds[0];
        var bottom = bounds[1];
        var right = bounds[2];
        var top = bounds[3];
        OpenLayers.loadURL("/location/locations_data",
            {'x1': left,
            'x2': right,
            'y1': bottom,
            'y2': top,
            'level': Grakon.getLevel()},
            null,
            Grakon.Utils.visualizeElectionCommissions,
            function() {
                OpenLayers.Console.error("Ошибка при загрузке избирательных комиссий для заданного квадрата.");
            }
        );
    },
    
    /**
     * По изменению масштабирования переключать слои
     */
    mapZoomEndHandler: function() {
        Grakon.Utils.removePopups();
        
        // границы регионов
        if (Grakon.borderLayers.regions != null)
            Grakon.borderLayers.regions.setVisibility( Grakon.getLevel() < 3 );
        
        // границы районов
        if (Grakon.borderLayers.districts != null)
        	Grakon.borderLayers.districts.setVisibility( Grakon.getLevel() == 3 );
            
        // видимость ИКСов
        if (Grakon.electionCommissionLayers.regions != null)
            Grakon.electionCommissionLayers.regions.setVisibility( Grakon.getLevel() > 1 );
            
        // видимость ТИКов
        if (Grakon.electionCommissionLayers.districts != null)
            Grakon.electionCommissionLayers.districts.setVisibility( Grakon.getLevel() > 2 );
            
        // видимость УИКов
        if (Grakon.electionCommissionLayers.areas != null)
            Grakon.electionCommissionLayers.areas.setVisibility( Grakon.getLevel() > 3 );
    },
    
    /**
     * Создаёт и добавляет слои на карту
     */
    initMapLayers: function() {        
        var Y_map = new OpenLayers.Layer.Yandex("Карта-схема от Яндекс", {type: YMaps.MapType.MAP, sphericalMercator: true});
        var Y_sat = new OpenLayers.Layer.Yandex("Вид со спутника от Яндекс",{type:YMaps.MapType.SATELLITE, sphericalMercator: true});
        var Y_hyb = new OpenLayers.Layer.Yandex("Гибридный вид от Яндекс",{type:YMaps.MapType.HYBRID, sphericalMercator: true});
        var OSM_map = new OpenLayers.Layer.OSM("Карта-схема от OpenStreetMap");
        
        Y_map.projection = Y_sat.projection = Y_hyb.projection = OSM_map.projection = new OpenLayers.Projection("EPSG:3857");
        
        Grakon.map.addLayer(Y_map);
        Grakon.map.addLayer(Y_sat);
        Grakon.map.addLayer(Y_hyb);
        Grakon.map.addLayer(OSM_map);
        
        // назначаем базовую карту
        var baseLayer = OSM_map;
        if ($.cookie('MAP_TYPE_INDEX') != null && Grakon.map.getLayersByName( $.cookie('MAP_TYPE_INDEX') ).length > 0)
            baseLayer = Grakon.map.getLayersByName( $.cookie('MAP_TYPE_INDEX') ).pop();
        Grakon.map.setBaseLayer(baseLayer);
        
        // запоминаем выбранную карту в cookie
        Grakon.map.events.register("changelayer", Grakon.map, Grakon.changeMapHandler );
        
        Grakon.addRegionBorders();
        Grakon.addDistrictBorders();
        Grakon.initElectionCommissionLayers();
    },
    
    /**
     * Создать векторный слой субъектов РФ с выделением цветом при действиях мыши и добавить его на карту
     */
    addRegionBorders: function() {          
        var regions = new OpenLayers.Layer.Vector("Границы субъектов РФ", {
            projection: new OpenLayers.Projection("EPSG:4326"),
            styleMap: new OpenLayers.StyleMap(Grakon.REGION_STYLES)
        });

        // выделять субъект РФ цветом при наведении мыши
        var highlightCtrl = new OpenLayers.Control.SelectFeature(regions, {
            hover: true,
            highlightOnly: true,
            renderIntent: "temporary",
            callbacks: {
                click: Grakon.Utils.clickRegionHandler
            }
        });
        Grakon.map.addControl(highlightCtrl);
        highlightCtrl.activate();

        // Добавить слой на карту
        Grakon.map.addLayer(regions);
        regions.setVisibility( Grakon.getLevel() < 3 );
        Grakon.borderLayers.regions = regions;

        // Загрузить данные на слой
        OpenLayers.loadURL(Grakon.MAP_URLS.regions, {}, Grakon.Utils, Grakon.Utils.addRegionBorders, function() {
            OpenLayers.Console.error("Ошибка при загрузке границ субъектов РФ");
        });
    },
    
    /**
     * Создать слои меток для ИКСов, ТИКов и УИКов
     */
    initElectionCommissionLayers: function() {
        // Добавим слой УИКи
        if (Grakon.electionCommissionLayers.areas == null) {
            var areasLayer = new OpenLayers.Layer.Markers( "УИКи" );
            Grakon.electionCommissionLayers.areas = areasLayer;
            Grakon.map.addLayer( areasLayer );
        }
        
        // Добавим слой ТИКи
        if (Grakon.electionCommissionLayers.districts == null) {
            var districtsLayer = new OpenLayers.Layer.Markers( "ТИКи" );
            Grakon.electionCommissionLayers.districts = districtsLayer;
            Grakon.map.addLayer( districtsLayer );
        }
        
        // Добавим слой ИКСы
        if (Grakon.electionCommissionLayers.regions == null) {
            var regionsLayer = new OpenLayers.Layer.Markers( "ИКСы" );
            Grakon.electionCommissionLayers.regions = regionsLayer;
            Grakon.map.addLayer( regionsLayer );
        }
    },
    
    addDistrictBorders: function() {            
        var districts = new OpenLayers.Layer.Vector("Границы районов", {
            projection: new OpenLayers.Projection("EPSG:4326"),
            styleMap: new OpenLayers.StyleMap(Grakon.DISTRICT_STYLES)
        });
        // Добавить слой на карту
        districts.setVisibility( Grakon.getLevel() == 3 );
        Grakon.borderLayers.districts = districts;
        
        // выделять субъект РФ цветом при наведении мыши
        var highlightCtrl = new OpenLayers.Control.SelectFeature(districts, {
            hover: true,
            highlightOnly: true,
            renderIntent: "temporary",
            callbacks: {
                click: Grakon.Utils.clickRegionHandler
            }
        });
        Grakon.map.addControl(highlightCtrl);
        highlightCtrl.activate();

        // Загрузить данные на слой
        OpenLayers.loadURL("/static/districts/48s.json", {}, Grakon.Utils, Grakon.Utils.addDistrictBorders, function() {
            OpenLayers.Console.error("Ошибка при загрузке районов субъекта РФ");
        });
        OpenLayers.loadURL("/static/districts/49s.json", {}, Grakon.Utils, Grakon.Utils.addDistrictBorders, function() {
            OpenLayers.Console.error("Ошибка при загрузке районов субъекта РФ");
        });
        
        Grakon.map.addLayer(districts);
    },
    
    /**
     * Добавляет инструменты управления на карту (например, масштабирование и выбор слоя)
     */
    initMapTools: function() {
        Grakon.map.addControl(new OpenLayers.Control.PanZoomBar());
        $('.olControlPanZoomBar').css('left', '14px');
        
        Grakon.map.addControl(new OpenLayers.Control.Navigation());
        Grakon.map.addControl(new OpenLayers.Control.MousePosition());
        
        // Добавить инструмент "ссылка на данный вид карты"
        Grakon.map.addControl(new OpenLayers.Control.Permalink());
        $(Grakon.map.div).find(".olControlPermalink > a").text("Ссылка на данный вид карты");
        
        // Создать и изменить стиль у переключателя слоёв
        Grakon.layerSwitcher = new OpenLayers.Control.LayerSwitcher();
        Grakon.map.addControl( Grakon.layerSwitcher );
        Grakon.layerSwitcher.baseLbl.innerHTML = "Карты";
        Grakon.layerSwitcher.dataLbl.style.marginTop = "20px";
        Grakon.layerSwitcher.dataLbl.innerHTML = "Данные";
        $('div.olControlLayerSwitcher').find('span').css('background-color', '#3980a3')
        if ($.cookie('MAP_TYPE_INDEX') == null)
            Grakon.layerSwitcher.maximizeControl();

        // Создать панель из кнопок
        var panel = new OpenLayers.Control.NavToolbar();
        var fullscreenBtn = new OpenLayers.Control.Button({
            type: OpenLayers.Control.TYPE_TOGGLE,
            title: "Развернуть карту на весь экран",
            displayClass: "fullscreenBtn",
            eventListeners: {
                activate: Grakon.resizeMap,
                deactivate: Grakon.resizeMap
            }
        });
        panel.addControls([fullscreenBtn]);
        Grakon.map.addControl(panel);
        
        Grakon.addStatisticsPanel();
    },
    
    addStatisticsPanel: function() {
        var votersBtn = new OpenLayers.Control.Button({
            type: OpenLayers.Control.TYPE_TOGGLE,
            title: "Показать количество избирателей на участках",
            displayClass: "voters",
            eventListeners: StatisticsButtonHandlers
        });
        
        var observersBtn = new OpenLayers.Control.Button({
            type: OpenLayers.Control.TYPE_TOGGLE,
            title: "Показать количество наблюдателей на участках",
            displayClass: "observers",
            eventListeners: StatisticsButtonHandlers
        });
        
        var journalistsBtn = new OpenLayers.Control.Button({
            type: OpenLayers.Control.TYPE_TOGGLE,
            title: "Показать количество представителей СМИ на участках",
            displayClass: "journalists",
            eventListeners: StatisticsButtonHandlers
        });
        
        var membersBtn = new OpenLayers.Control.Button({
            type: OpenLayers.Control.TYPE_TOGGLE,
            title: "Показать количество членов избирательных комиссий",
            displayClass: "members",
            eventListeners: StatisticsButtonHandlers
        });
        
        var authoritiesBtn = new OpenLayers.Control.Button({
            type: OpenLayers.Control.TYPE_TOGGLE,
            title: "Показать количество представителей власти на участках",
            displayClass: "authorities",
            eventListeners: StatisticsButtonHandlers
        });
        
        var prosecutorsBtn = new OpenLayers.Control.Button({
            type: OpenLayers.Control.TYPE_TOGGLE,
            title: "Показать количество представителей прокуратуры на участках",
            displayClass: "prosecutors",
            eventListeners: StatisticsButtonHandlers
        });
        
        var statisticsPanel = new OpenLayers.Control.Panel();
        
        statisticsPanel.addControls([votersBtn, observersBtn, journalistsBtn, membersBtn/*, authoritiesBtn, prosecutorsBtn*/]);
        Grakon.map.addControl(statisticsPanel);
    },
    
    /**
     * Разворачивает карту на весь экран (или восстанавливает в прежних размерах)
     */
    resizeMap: function() {
        var relative = ($(Grakon.map.div).css('position') != "fixed");
        var height = (relative) ? "100%" : 500;
        $(Grakon.map.div).css({
            position: relative ? 'fixed' : 'relative',
            left: 0,
            top: relative ? 51 : 0,
            width: "100%", 
            height: height
        });
        Grakon.map.updateSize();
    },
    
    /**
     * @returns номер уровня показываемых избирательных комиссий [от 1 до 4]
     */
    getLevel: function() {
        var level = 1;
        if (Grakon.map.getZoom() >= Grakon.MAP_LEVELS_ZOOM.areas)
            level = 4;
        else if (Grakon.map.getZoom() >= Grakon.MAP_LEVELS_ZOOM.districts)
            level = 3;
        else if (Grakon.map.getZoom() >= Grakon.MAP_LEVELS_ZOOM.regions)
            level = 2
        return level;
    },

    /**
     * Приблизить карту к заданным координатам.
     * @param {lon} долгота
     * @param {lat} широта
     * @param {type} тип избирательной комиссии
     */
    zoomOnElectionCommission: function(lon, lat, type) {
        var nextZoom;
        var defaultZoom = Grakon.Utils.getZoomForLevel(type);
                
        if (Grakon.map.getZoom() >= Grakon.MAP_LEVELS_ZOOM.max)
            nextZoom = defaultZoom;
        else if (Grakon.getLevel() >= 4)
            nextZoom = Grakon.MAP_LEVELS_ZOOM.max;
        else
            nextZoom = Grakon.Utils.getZoomForLevel( Grakon.getLevel()+1 );
        
        var center = new OpenLayers.LonLat(lon, lat).transform(new OpenLayers.Projection("EPSG:4326"), Grakon.map.getProjectionObject());
        Grakon.map.setCenter(center, nextZoom);
    },
    
    /**
     * Сохраняет выбранную карту в cookie
     * @param {event} объект с аттрибутами layer и property
     */
    changeMapHandler: function(event) {
        if (event.property != 'visibility' || !event.layer['visibility'] ||
            event.layer == null || Grakon.layerSwitcher == null)
                return;
        
        for (var n in Grakon.layerSwitcher.baseLayers)
            if (Grakon.layerSwitcher.baseLayers[n].layer == event.layer) {
                $.cookie('MAP_TYPE_INDEX', event.layer.name, {expires: 92, path: '/'});
                return;
            }
    }
};



/** 
 * @requires OpenLayers/Marker.js 
 * 
 * Class: OpenLayers.Marker.LabelMarker 
 * 
 * Inherits from: 
 *  - <OpenLayers.Marker>
 */ 
OpenLayers.Marker.LabelMarker = OpenLayers.Class(OpenLayers.Marker, { 

    /** 
     * Property: label 
     * {String} Marker label. 
     */ 
    label: "", 

    markerDiv: null,
                                                 
    labelOffset: null,

    initialize: function(lonlat, icon, label) { 
        OpenLayers.Marker.prototype.initialize.apply(this, [lonlat, icon]); 

        this.label = label;
        this.labelOffset = icon.offset;
        this.markerDiv = OpenLayers.Util.createDiv();
        this.markerDiv.appendChild(this.icon.imageDiv); 
        OpenLayers.Util.modifyDOMElement(this.icon.imageDiv, null, icon.offset); 
        var txtDiv = OpenLayers.Util.createDiv(); 
        txtDiv.className = 'markerLabel'; 
        OpenLayers.Util.modifyDOMElement(txtDiv, null, this.labelOffset); 
        txtDiv.innerHTML = this.label; 
        this.markerDiv.appendChild(txtDiv); 
    },

    /** 
     * Method: destroy 
     * Nullify references and remove event listeners to prevent circular 
     * references and memory leaks 
     */ 
    destroy: function() { 
        OpenLayers.Marker.prototype.destroy.apply(this, arguments); 
        this.markerDiv.innerHTML = ""; 
        this.markerDiv = null; 
    }, 

    draw: function(px) { 
        OpenLayers.Util.modifyAlphaImageDiv(this.icon.imageDiv, 
                                            null, 
                                            null, 
                                            this.icon.size, 
                                            this.icon.url); 

        OpenLayers.Util.modifyDOMElement(this.markerDiv, null, px); 
        return this.markerDiv; 
    }, 

    redraw: function(px) { 
        if ((px != null) && (this.markerDiv != null)) { 
            OpenLayers.Util.modifyDOMElement(this.markerDiv, null, px); 
        } 
    }, 

    moveTo: function (px) { 
        this.redraw(px); 
        this.lonlat = this.map.getLonLatFromLayerPx(px); 
    }, 

    isDrawn: function() { 
        return false; 
    }, 

    CLASS_NAME: "OpenLayers.Marker.LabelMarker" 
});