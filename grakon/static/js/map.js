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
	
	// Переменная, в которой заданы все типы масштабирования для карты.
	MAP_LEVELS: new Array(
        {index: 0, value: "ЦИК"},
        {index: 4, value: "ИКСы"},
        {index: 10, value: "ТИКи"}
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

		ElectionMap.map = new YMaps.Map( document.getElementById("publicElectionsMap") );
		ElectionMap.map.setType(YMaps.MapType.PMAP);
		ElectionMap.map.enableScrollZoom();

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
		ElectionMap.map.addControl(new YMaps.SearchControl({/*geocodeOptions: {geocodeProvider: "yandex#pmap"}, */width: 400}));
		
		// Показать на карте заданное место
		ElectionMap.setDefaultViewport(place);

		ElectionMap.addButtons();
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
			usermark.description = "Ваше предположительное местоположение";
			ElectionMap.map.addOverlay(usermark);
		}
		// Показываем заданное место на карте.
		if (place == null || place == "") { // Если место не задано, то для пользователя из России будет определено его местоположение и показано на карте с максимальным масштабом;
											// для пользователя из-за рубежа карта будет отцентрована по европейской части России.
            var zoom = 4;
			var center = new YMaps.GeoPoint(37.64, 55.76);
			
			if (YMaps.location && YMaps.location.country == "Россия") {
				center = new YMaps.GeoPoint(YMaps.location.longitude, YMaps.location.latitude);
				zoom = YMaps.location.zoom;
			}
			
			ElectionMap.map.setCenter(center, zoom);
			// Считаем все избирательные комиссии на карте
			ElectionMap.markElectionCommissions();
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
	},

    markElectionCommission: function(commission) {
        // создаём метку для избирательной комиссии с именем и описанием
        var geoPoint = new YMaps.GeoPoint(commission.xCoord, commission.yCoord);
        var placemark = new YMaps.Placemark(geoPoint);
        placemark.name = commission.title;
        placemark.description = commission.address +
                ' <a href="#" onclick="ElectionMap.showComission(\''+commission+'\', true); return false;"><img src="/static/images/target.png" alt="Цель" title="Найти на карте" style="position: relative; bottom: -3px;" /></a>' +
                ((commission.numVoters != null && commission.numVoters > 0) ?"Избирателей: "+commission.numVoters+"<br/>":"") +
                ((commission.numObservers != null && commission.numObservers > 0) ?"Наблюдателей: "+commission.numObservers+"<br/>":"") +
                ('<p><a href="/location/'+commission.id+'">Станица округа</a></p>');
        placemark.setIconContent(commission.shortTitle);
        placemark.id = commission.id;
        placemark.level = commission.level;
        placemark.data = commission.data;
        //placemark.shortTitle = commission.shortTitle;
        ElectionMap.placemarks[commission.level-1].push(placemark);

        ElectionMap.checkForVisibility(placemark);
        ElectionMap.showElectionCommissionMarks();
    },

	showComission: function(comission) {
        // TODO: fix it
        ElectionMap.map.setBounds(this.get(0).getBounds());
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
	showElectionCommissionMarks: function() {
		// Создание диспетчера объектов и добавление его на карту
		var objManager = new YMaps.ObjectManager();
		ElectionMap.map.addOverlay(objManager);
		for (var num=0; num < ElectionMap.placemarks.length; num++)
			if (num < ElectionMap.MAP_LEVELS.length)
				objManager.add(
					ElectionMap.placemarks[num],
					ElectionMap.MAP_LEVELS[num].index,
					19
				);
		
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
			ElectionMap.electionCommissionLevel == placemark.level) {
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