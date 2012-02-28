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
    
    AREA_DISTRICT_STYLES: {
        'default':  new OpenLayers.Style({
                      'fillColor': '#000000',
                      'fillOpacity': 0,
                      'strokeColor': '#000000',
                      'strokeOpacity': 0.75,
                      'strokeWidth': 2,
                      'strokeDashstyle': 'dot'
                    }),
        'temporary':    new OpenLayers.Style({
                      'fillColor': '#000000',
                      'fillOpacity': 0,
                      'strokeColor': '#ee9900',
                      'strokeOpacity': 1,
                      'strokeWidth': 2,
                      'strokeDashstyle': 'dot'
                    }),
        'select':   null
    },
    
    /**
     * @private
     * Объект OpenLayers.Map — используемая карта.
     */
    map: null,
    mapZoomBeforeMove: null,
    moscowBounds: new OpenLayers.Bounds(37.22, 55.48, 37.95, 56.03).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913")),
    
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
    },
    
    ELECTION_COMMISSION_IMAGES: new Object({
        2: "/static/images/iks.png",
        3: "/static/images/tik.png",
        4: "/static/images/uik.png"
    }),
    
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
        AutoSizeFramedCloudMaxSize: OpenLayers.Class(OpenLayers.Popup.FramedCloud, {
            'autoSize': true, 
            'maxSize': new OpenLayers.Size(480,480)
        }),
        
        currentPopup: null,
        
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
        },
        
        /**
         * Загружаем УИКи для заданного квадрата и показываем их на слое "УИКи"
         * @private
         * @param {request} Объект XMLHttpRequest с результатами в виде массива JS из объектов ElectionCommission.
         */
        loadCommissionsForBBOX: function(request) {
            if (request.status == 200) {
                if (request.responseText == "error")
                    return;
                eval(request.responseText);
                if (electionCommissions) {
                    Grakon.initElectionCommissionLayers();
                    // Добавим новые (не показанные) избирательные комиссии на карту
                    for (var id in electionCommissions)
                        if (Grakon.electionCommissions[id] == null) {
                            Grakon.electionCommissions[id] = id;
                            var location = new OpenLayers.LonLat(electionCommissions[id].xCoord,electionCommissions[id].yCoord).transform(new OpenLayers.Projection("EPSG:4326"), Grakon.map.getProjectionObject());
                            var popupContentHTML = Grakon.Utils.buildElectionCommissionMarkerContent(electionCommissions[id]);
                            Grakon.Utils.addMarker(electionCommissions[id].level, location, popupContentHTML, electionCommissions[id].data);
                        }
                }
            } else
                OpenLayers.Console.error("Запрос избирательных комиссий для заданного квадрата вернул статус: " + request.status);
        },
        
        /**
         * @param {electionCommission} объект класса ElectionCommission
         * @returns строку HTML используемую в качестве контента для всплывающей подсказки на метке
         */
        buildElectionCommissionMarkerContent: function(electionCommission) {
            var type;
            switch(electionCommission.level) {
              case 1: type = '<span class="commissionType">Центральная Избирательная Комиссия</span><br/>'; break;
              case 2: type = '<span class="commissionType">Избирательная Комиссия Субъекта РФ</span><br/>'; break;
              case 3: type = '<span class="commissionType">Территориальная Избирательная Комиссия</span><br/>'; break;
              case 4: type = '<span class="commissionType">Участковая Избирательная Комиссия</span><br/>'; break;
            }
            var address = '<span class="address">'+electionCommission.address+'</span>';
            var title = ((electionCommission.level == 4) ? "УИК №" : "") + electionCommission.title;
            var content = "<h3>"+title+"</h3>";
            content += "<p>"+type+address+"</p>"
            if (electionCommission.data != null) {
                content += "<p>";
                content += (electionCommission.data.voters != null) ? "Избирателей: " + electionCommission.data.voters + "<br/>" : "";
                content += (electionCommission.data.observers != null) ? "Наблюдателей: " + electionCommission.data.observers + "<br/>" : "";
                content += (electionCommission.data.members != null) ? "Членов комисии: " + electionCommission.data.members + "<br/>" : "";
                content += (electionCommission.data.journalists != null) ? "Представителей СМИ: " + electionCommission.data.journalists + "<br/>" : "";
                content += "</p>";
            }
            content += '<p><a href="/location/'+electionCommission.id+'">Страница комиссии</a></p>';
            return content;
        },
        
        removePopups: function() {
            if (Grakon.Utils.currentPopup != null) {
                Grakon.Utils.currentPopup.toggle();
                Grakon.map.removePopup( Grakon.Utils.currentPopup );
            }
        },
        
        /**
         */
        addMarker: function(level, location, content, data) {
            var markers;
            switch(level) {
                case 2: layer = Grakon.electionCommissionLayers.regions; break;
                case 3: layer = Grakon.electionCommissionLayers.districts; break;
                case 4: layer = Grakon.electionCommissionLayers.areas; break;
                default: return;
            }
            
            var feature = new OpenLayers.Feature(layer, location, data); 
            feature.closeBox = true;
            feature.popupClass = Grakon.AutoSizeFramedCloudMaxSize;
            feature.data.popupContentHTML = content;
            feature.data.overflow = "auto";
            feature.data.icon = new OpenLayers.Icon(
                Grakon.ELECTION_COMMISSION_IMAGES[level],
                new OpenLayers.Size(18, 32),
                new OpenLayers.Pixel(-9, -32));
                    
            var marker = feature.createMarker();
 
            var markerClick = function (evt) {
                Grakon.Utils.removePopups();
                
                if (this.popup == null) {
                    this.popup = this.createPopup(this.closeBox);
                    Grakon.map.addPopup(this.popup);
                    this.popup.show();
                } else {
                    this.popup.toggle();
                }
                Grakon.Utils.currentPopup = this.popup;
                OpenLayers.Event.stop(evt);
            };
            marker.events.register("mousedown", feature, markerClick);
 
            layer.addMarker(marker);
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
        
        // слушаем событие начала масштабирования
        Grakon.map.events.register("movestart", Grakon.map, function () {
            Grakon.mapZoomBeforeMove = Grakon.map.getZoom();
        });
        
        // слушаем событие окончания масштабирования
        Grakon.map.events.register("zoomend", Grakon.map, Grakon.mapZoomEndHandler);
        
        // слушаем событие окончания перемещения по карте
        Grakon.map.events.register("moveend", Grakon.map, function() {
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
                Grakon.Utils.loadCommissionsForBBOX,
                function() {
                    OpenLayers.Console.error("Ошибка при загрузке избирательных комиссий для заданного квадрата.");
                }
            );
        });
    },
    
    /**
     * По изменению масштабирования переключать слои
     */
    mapZoomEndHandler: function() {
        Grakon.Utils.removePopups();
        
        // границы регионов
        if (Grakon.borderLayers.regions != null)
            Grakon.borderLayers.regions.setVisibility( Grakon.getLevel() > 1 );
        
        // границы районов
        if (Grakon.borderLayers.districts != null) {
            if (Grakon.getLevel() > 2) {
                Grakon.borderLayers.districts.setVisibility( true );
                var styles = (Grakon.getLevel() > 3) ? Grakon.AREA_DISTRICT_STYLES : Grakon.DISTRICT_STYLES;
                if (Grakon.borderLayers.districts.styleMap != styles) {
                    Grakon.borderLayers.districts.styleMap = new OpenLayers.StyleMap(styles);
                    Grakon.borderLayers.districts.redraw();
                }
            } else
                Grakon.borderLayers.districts.setVisibility( false );
        }
            
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
        var Y_map = new OpenLayers.Layer.Yandex("Карта-схема от Яндекс",{sphericalMercator: true});
        var Y_sat = new OpenLayers.Layer.Yandex("Вид со спутника от Яндекс",{type:YMaps.MapType.SATELLITE, sphericalMercator:true});
        var Y_hyb = new OpenLayers.Layer.Yandex("Гибридный вид от Яндекс",{type:YMaps.MapType.HYBRID, sphericalMercator:true});
        var OSM_map = new OpenLayers.Layer.OSM("Карта-схема от OpenStreetMap");
        Grakon.map.addLayer(Y_map);
        Grakon.map.addLayer(OSM_map);
        Grakon.map.addLayer(Y_sat);
        Grakon.map.addLayer(Y_hyb);
        Grakon.map.setBaseLayer(Y_map);
        
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
        regions.setVisibility( Grakon.getLevel() > 1 );
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
        districts.setVisibility( Grakon.getLevel() > 2 );
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
        Grakon.map.addControl(new OpenLayers.Control.LayerSwitcher());
        Grakon.map.addControl(new OpenLayers.Control.Navigation());
        Grakon.map.addControl(new OpenLayers.Control.MousePosition());
        
        var button = new OpenLayers.Control.Button({
            displayClass: "Test", trigger: function() {alert("True");}
        });
        var panel = new OpenLayers.Control.Panel({defaultControl: button});
        panel.addControls([button]);
        Grakon.map.addControl(panel);
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
    }
};