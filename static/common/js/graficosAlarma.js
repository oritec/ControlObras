var GraficosAlarma = function() {
	var data_chart_1=[];
	var data_chart_2=[];

	var initChart1 = function() {
    	var chart = AmCharts.makeChart("chart_1", {
            "type": "pie",
            "theme": "light",
            "pathToImages": "static/common/assets/global/plugins/amcharts/amcharts/images/",

            "fontFamily": 'Open Sans',
            "color":    '#888',
            'colors':["#4b87ff", "#FF6600", "#FF9E01", "#008496", "#F8FF01",
                      "#B0DE09", "#04D215", "#0D8ECF", "#0D52D1", "#2A0CD0",
                      "#8A0CCF", "#CD0D74", "#754DEB", "#DDDDDD", "#999999",
                      "#333333", "#000000", "#57032A", "#CA9726", "#990000", "#4B0C25"],


            "dataProvider": data_chart_1,


            "valueField": "cuenta",
            "titleField": "alarma",
            "descriptionField" : "nombre",
            "outlineAlpha": 0.4,
            "depth3D": 15,
            "balloonText": "Cuenta = [[value]]<br><span style='font-size:14px'><b>[[nombre]]</b> ([[percents]]%)</span>",
            "labelText":"Alarma Nº [[title]]: [[percents]]%",
            "angle": 30,
            "thousandsSeparator":".",
            "decimalSeparator":",",

        });

        $('#chart_1').closest('.portlet').find('.fullscreen').click(function() {
            chart.invalidateSize();
        });
    }

    var initChart2 = function() {
    	var chart = AmCharts.makeChart("chart_2", {
            "type": "pie",
            "theme": "light",
            "pathToImages": "static/common/assets/global/plugins/amcharts/amcharts/images/",

            "fontFamily": 'Open Sans',
            "color":    '#888',
            'colors':["#4b87ff", "#FF6600", "#FF9E01", "#008496", "#F8FF01",
                      "#B0DE09", "#04D215", "#0D8ECF", "#0D52D1", "#2A0CD0",
                      "#8A0CCF", "#CD0D74", "#754DEB", "#DDDDDD", "#999999",
                      "#333333", "#000000", "#57032A", "#CA9726", "#990000", "#4B0C25"],


            "dataProvider": data_chart_2,


            "valueField": "duracion",
            "titleField": "alarma",
            "descriptionField" : "printable",
            "outlineAlpha": 0.4,
            "depth3D": 15,
            "balloonText": "Duración total = [[description]]<br><span style='font-size:14px'><b>[[nombre]]</b> ([[percents]]%)</span>",
            "labelText":"Alarma Nº [[title]]: [[percents]]%",
            "angle": 30,
            "thousandsSeparator":".",
            "decimalSeparator":",",
            "zoomOutOnDataUpdate" : false,
        });

        $('#chart_2').closest('.portlet').find('.fullscreen').click(function() {
            chart.invalidateSize();
        });
    }

    var initChart3 = function() {
    	var chart = AmCharts.makeChart("chart_3", {
            "type": "pie",
            "theme": "light",
            "pathToImages": "static/common/assets/global/plugins/amcharts/amcharts/images/",

            "fontFamily": 'Open Sans',
            "color":    '#888',
            'colors':["#4b87ff", "#FF6600", "#FF9E01", "#008496", "#F8FF01",
                      "#B0DE09", "#04D215", "#0D8ECF", "#0D52D1", "#2A0CD0",
                      "#8A0CCF", "#CD0D74", "#754DEB", "#DDDDDD", "#999999",
                      "#333333", "#000000", "#57032A", "#CA9726", "#990000", "#4B0C25"],


            "dataProvider": data_chart_3,


            "valueField": "duracion",
            "titleField": "alarma",
            "descriptionField" : "printable",
            "outlineAlpha": 0.4,
            "depth3D": 15,
            "balloonText": "Energía total = [[description]]<br><span style='font-size:14px'><b>[[nombre]]</b> ([[percents]]%)</span>",
            "labelText":"Alarma Nº [[title]]: [[percents]]%",
            "angle": 30,
            "thousandsSeparator":".",
            "decimalSeparator":",",
            "zoomOutOnDataUpdate" : false,
        });

        $('#chart_3').closest('.portlet').find('.fullscreen').click(function() {
            chart.invalidateSize();
        });
    }

    return {
        //main function to initiate the module
    	init: function(data){
    		data_chart_1=data[0];
    		data_chart_2=data[1];
    		data_chart_3=data[2];
    	},
        show: function() {
            initChart1();
            initChart2();
            initChart3();
        }
    };
}();