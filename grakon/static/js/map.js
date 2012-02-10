/**
 * Класс для избирательных округов
 * @param {level} уровень избирательного округа (от 1 до 3)
 * @param {data} объект типа {numVoters: 4, numObservers: 6}
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

/**
 * Именованная область видимости для общественной карты выборов.
 */
var ElectionMap = {
	map: null,

	placemarks: null,

    buttons: null,

    electionCommissionLevel: null,

    visibleElectionCommissions: new Array(),

    centerNearestElectionCommission: null,

    distanceToNearestElectionCommission: null,

    objManager: new YMaps.ObjectManager(),

    placemarkStyles: new Array(),

	// Переменная, в которой заданы все типы масштабирования для карты.
	MAP_LEVELS: new Array(
        {index: 2, value: "ЦИК"},
        {index: 6, value: ""},
        {index: 12, value: "ТИКи"},
        {index: 4, value: "ИКСы"}
	),

	/**
	 * Добавляем Народную Яндекс.Карту на страницу и отмечаем на ней все избирательные комиссии.
	 * @param {place} название области или района, который показать следует показать по-умолчанию.
	 * Задать null, чтобы показать пользователю из России его местоположение,
	 * а для заграничного пользователя показать европейскую часть России.
	 * @param {electionCommissionLevel} указывает уровень избирательной комиссии, которая должна попасть в масштаб карты по-умолчанию.
	 */
	init: function(place, electionCommissionLevel) {
		if (electionCommissionLevel != null && electionCommissionLevel != "")
			ElectionMap.electionCommissionLevel =  electionCommissionLevel;

        ElectionMap.initPlacemarkStyles();

		ElectionMap.map = new YMaps.Map( document.getElementById("publicElectionsMap") );
		ElectionMap.map.setType(YMaps.MapType.HYBRID);
		ElectionMap.map.setMinZoom(2);

		// Переименовываем типы карт, чтобы их можно было различать. Народные карты имеют индекс 1, обычные - индекс 2.
		YMaps.MapType.PMAP.setName("Схема 1");
		YMaps.MapType.MAP.setName("Схема 2");
		YMaps.MapType.PHYBRID.setName("Гибрид 1");
		YMaps.MapType.HYBRID.setName("Гибрид 2");
		ElectionMap.map.addControl(new YMaps.TypeControl(
            [YMaps.MapType.PMAP, YMaps.MapType.MAP, YMaps.MapType.SATELLITE, YMaps.MapType.PHYBRID, YMaps.MapType.HYBRID,],
            [0,1,2,3,4]
        )); // объявляем доступные типы карт
		ElectionMap.map.addControl(new YMaps.ToolBar());
		ElectionMap.map.addControl(new YMaps.Zoom({customTips: ElectionMap.MAP_LEVELS}));
		ElectionMap.map.addControl(new YMaps.SearchControl({width: (place == null || place == "") ? 400 : 200}));
		
		ElectionMap.map.addOverlay( ElectionMap.objManager );
		// Показать на карте заданное место
		ElectionMap.setDefaultViewport(place);

		//ElectionMap.addButtons();
	},

    /**
      * Создаём стили для меток избирательных комиссий
      */
    initPlacemarkStyles: function() {
        var s = new YMaps.Style();
        s.iconStyle = new YMaps.IconStyle();
        s.iconStyle.href = "/static/images/election_commission.png";
        s.iconStyle.size = new YMaps.Point(24, 28);
        s.iconStyle.offset = new YMaps.Point(-17, -19);

        ElectionMap.placemarkStyles.push(s);
        ElectionMap.placemarkStyles.push("default#orangePoint");
        ElectionMap.placemarkStyles.push("default#lightbluePoint");
    },

	/**
	 * Центрирует карту на указанном месте с оптимальным масштабом.
	 * @param {place} - место, которое будет показано на карте. Если не задано, то будет показана вся Россия
	 */
	setDefaultViewport: function(place) {
		// Определяем координаты пользователя и отмечаем на карте
		if (YMaps.location) {
			var userLocation = new YMaps.GeoPoint(YMaps.location.longitude, YMaps.location.latitude);
			// Создание стиля для значка пользователя
			var s = new YMaps.Style();
			s.iconStyle = new YMaps.IconStyle();
			s.iconStyle.href = "/static/images/user.png";
			s.iconStyle.size = new YMaps.Point(32, 32);
			s.iconStyle.offset = new YMaps.Point(-16, -16);
			// Создание метки и добавление пользователя на карту
			var usermark = new YMaps.Placemark(userLocation, {style: s, hideIcon: false});
			usermark.description = "Ваше местоположение";
			ElectionMap.map.addOverlay(usermark);
		}

		var zoom = ElectionMap.MAP_LEVELS[3].index;
        var center = new YMaps.GeoPoint(37.64, 55.76);

		// Показываем заданное место на карте.
		if (place == null || place == "") { // Если место не задано, то для пользователя из России будет определено его местоположение и показано на карте с максимальным масштабом;
											// для пользователя из-за рубежа карта будет отцентрована по европейской части России.
            ElectionMap.map.enableScrollZoom();

			if (YMaps.location && YMaps.location.country == "Россия") {
				center = new YMaps.GeoPoint(YMaps.location.longitude, YMaps.location.latitude);
				zoom = YMaps.location.zoom;
			}
			
			ElectionMap.map.setCenter(center, zoom);
			// Считаем все избирательные комиссии на карте
			ElectionMap.markElectionCommissions();
		} else {
			var geocoder = new YMaps.Geocoder(place, {geocodeProvider: "yandex#map"});
			// Создает обработчик успешного завершения геокодирования
			YMaps.Events.observe(geocoder, geocoder.Events.Load, function () {
				// Если объект найден, устанавливает центр карты в центр области показа объекта
				if (this.length()) {
					ElectionMap.map.setBounds(this.get(0).getBounds());
					ElectionMap.markElectionCommissions();
				} else
					ElectionMap.map.setCenter(center, zoom);
			});

			// Процесс геокодирования завершен с ошибкой
			YMaps.Events.observe(geocoder, geocoder.Events.Fault, function (gc, error) {
				alert("Произошла ошибка: " + error);
			});
		}
	},

	/**
	 * Отмечает на карте все избирательные комиссии.
	 */
	markElectionCommissions: function() {
		// Define an election commissions collection for three types of election commissions
		ElectionMap.placemarks = new Array(new Array(), new Array(), new Array());

		for (var n in electionCommissions)
			ElectionMap.markElectionCommission(electionCommissions[n]);
			
		ElectionMap.resetZoom();
	},

    markElectionCommission: function(commission) {
        // создаём метку для избирательной комиссии с именем и описанием
        var geoPoint = new YMaps.GeoPoint(commission.xCoord, commission.yCoord);
        var styleValue = ElectionMap.placemarkStyles[commission.level-1];
        var placemark = new YMaps.Placemark(geoPoint, {style: styleValue});
        placemark.name = '<a href="#" onclick="ElectionMap.showRegion(\''+commission.id+'\')" title="Показать данную область на карте" style="color: black">'+commission.title+'</a>';
        placemark.description = commission.address +
                //((commission.numVoters != null && commission.numVoters > 0) ?"Избирателей: "+commission.numVoters+"<br/>":"") +
                //((commission.numObservers != null && commission.numObservers > 0) ?"Наблюдателей: "+commission.numObservers+"<br/>":"") +
                ('<p><a href="/location/'+commission.id+'">Страница округа</a></p>');
        placemark.data = commission;

        // добавить значки избирательных комиссий на карту
        if (commission.level == 2)
            ElectionMap.addElectionCommissionIcon(placemark);

        placemark.setIconContent( commission.shortTitle );

        ElectionMap.placemarks[commission.level-1].push(placemark);
        ElectionMap.objManager.add(placemark, ElectionMap.MAP_LEVELS[commission.level-1].index, 19);

        ElectionMap.checkForVisibility(placemark);
    },

    /**
     * Добавляет иконку избирательной комиссии на карту
     * @param {placemark} объект YMaps.Placemark
     */
    addElectionCommissionIcon: function(placemark) {
        var icon = new YMaps.Placemark(placemark.getGeoPoint(), {style: ElectionMap.placemarkStyles[0],
                                    hasHint: true,
                                    hideIcon: false});
        icon.name = placemark.name;
        icon.description = placemark.description;
        icon.setHintContent(placemark.data.shortTitle);
        ElectionMap.objManager.add(
            icon,
            ElectionMap.MAP_LEVELS[3].index,
            ElectionMap.MAP_LEVELS[1].index-1
        );
    },

    /**
     * Ищет и показывает на карте заданную область с максимальный масштабом.
     * @param {commissionId} id комиссии
    */
    showRegion: function(commissionId) {
        var commission = electionCommissions[commissionId];
        var point = new YMaps.GeoPoint(commission.xCoord, commission.yCoord);
        var zoom = (commission.level-1 < ElectionMap.MAP_LEVELS.length-2) ? ElectionMap.MAP_LEVELS[commission.level].index : 15;
        ElectionMap.map.setCenter(point, zoom);
    },

	/**
	 * Добавляет на карту 2 кнопки "Изибиратели", "Наблюдатели".
	 */
	addButtons: function() {
		var button;
		var buttons = new Array();

		// Кнопка "Избиратели"
        button = new YMaps.ToolBarButton({
            caption: "Избиратели",
            hint: "Показывает количество избирателей на избирательных округах"
        });
        button.dataType = "numVoters";
		YMaps.Events.observe(button, button.Events.Click, ElectionMap.buttonClick, buttons);
		buttons.push( button );

		// Кнопка "Наблюдатели"
		button = new YMaps.ToolBarButton({
            caption: "Наблюдатели",
            hint: "Показывает количество наблюдателей на избирательных округах"
        });
        button.dataType = "numObservers";
		YMaps.Events.observe(button, button.Events.Click, ElectionMap.buttonClick, buttons);
		buttons.push( button );

		ElectionMap.map.addControl(new YMaps.ToolBar(buttons),
                new YMaps.ControlPosition(YMaps.ControlPosition.BOTTOM_LEFT, new YMaps.Point(20, 20)));
	},

    buttonClick: function(button){
        if (button.isSelected()) {
            for (var num in ElectionMap.placemarks)
                for (var i in ElectionMap.placemarks[num])
                    ElectionMap.placemarks[num][i].setIconContent(ElectionMap.placemarks[num][i].shortTitle);
            button.deselect()
        } else {
            for (var num in ElectionMap.placemarks)
                for (var i in ElectionMap.placemarks[num])
                    ElectionMap.placemarks[num][i].setIconContent(ElectionMap.placemarks[num][i].data[button.dataType]);
            for (var num in this)
                this[num].deselect();
            button.select();
        }
    },

	/**
	 * Определяет и показывает на карте нужный уровень избирательных комиссий согласно масштабу.
	 */
	resetZoom: function() {
		while (ElectionMap.visibleElectionCommissions.length == 0 && ElectionMap.map.getZoom() >= 0) {
			ElectionMap.map.zoomBy(-1);
			ElectionMap.checkForVisibility( ElectionMap.centerNearestElectionCommission );
		}
	},

	/**
	 * @param {placemark} [YMaps.Placemark] метка для проверки на видимость в заданном масштабе карты
	 */
	checkForVisibility: function(placemark) {
		if (ElectionMap.map.getBounds() == null)
			return;

		if (ElectionMap.electionCommissionLevel == null ||
			ElectionMap.electionCommissionLevel == placemark.data.level) {
				// Проверить метку на видимость и в положительном случае сохранить в массив видимых избирательных комиссий
				if (ElectionMap.map.getBounds().contains( placemark.getCoordPoint() ))
					ElectionMap.visibleElectionCommissions.push( placemark );

				// Найти ближайшую избирательную комиссию к центру карты
				var mapCenter = new YMaps.GeoPoint(ElectionMap.map.getCenter().getX(), ElectionMap.map.getCenter().getY());
				var distanceToElectionCommission = mapCenter.distance( placemark.getGeoPoint() );
				if (ElectionMap.distanceToNearestElectionCommission == null ||
					distanceToElectionCommission < ElectionMap.distanceToNearestElectionCommission) {
						ElectionMap.distanceToNearestElectionCommission = distanceToElectionCommission;
						ElectionMap.centerNearestElectionCommission = placemark;
				}
		}
	}
};