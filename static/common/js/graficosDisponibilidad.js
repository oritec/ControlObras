var GraficosDisponibilidad = function() {
	var data_chart_1=[];

	var initChart1 = function() {
    	var chart = AmCharts.makeChart("chart_1", {
            "type": "serial",
            "theme": "light",
            "pathToImages": "static/common/assets/global/plugins/amcharts/amcharts/images/",

            "fontFamily": 'Open Sans',
            "color":    '#888',
            'colors':["#f8d02e", "#2cc3a5", "#a467bc", "#a0aeaf", "#d56667",
                      "#96ccf4", "#04D215", "#0D8ECF", "#0D52D1", "#2A0CD0",
                      "#8A0CCF", "#CD0D74", "#754DEB", "#DDDDDD", "#999999",
                      "#333333", "#000000", "#57032A", "#CA9726", "#990000", "#4B0C25"],


            "dataProvider": data_chart_1,

            "dataDateFormat": "YYYY-MM-DD",

            "legend": {
                "horizontalGap": 10,
                "useGraphSettings": true,
                "markerSize": 10
              },
            "decimalSeparator": ",",
            "thousandsSeparator": ".",
            "precision": 2,

            "graphs": [{
                "balloonText": "Disponibilidad [[title]] : <b>[[value]] %</b>",
                //"fillAlphas": 0.4,
                "fillAlphas": 0.9,
                "lineAlpha": 0.3,
                "type": "column",
                "color": "#000000",
                //"fillColors": "#c0c0c0",
                //"dashLength":5,
                //"lineThickness" : 8,
                "title": "Aerogenerador 1",
                "valueField": "WTG01"

            },{
                "balloonText": "Disponibilidad [[title]] : <b>[[value]] %</b>",
                //"fillAlphas": 0.4,
                "fillAlphas": 0.9,
                "lineAlpha": 0.3,
                "type": "column",
                "color": "#000000",
                //"fillColors": "#c0c0c0",
                //"dashLength":5,
                //"lineThickness" : 8,
                "title": "Aerogenerador 2",
                "valueField": "WTG02"

            },{
                "balloonText": "Disponibilidad [[title]] : <b>[[value]] %</b>",
                //"fillAlphas": 0.4,
                "fillAlphas": 0.9,
                "lineAlpha": 0.3,
                "type": "column",
                "color": "#000000",
                //"fillColors": "#c0c0c0",
                //"dashLength":5,
                //"lineThickness" : 8,
                "title": "Aerogenerador 3",
                "valueField": "WTG03"

            },{
                "balloonText": "Disponibilidad [[title]] : <b>[[value]] %</b>",
                //"fillAlphas": 0.4,
                "fillAlphas": 0.9,
                "lineAlpha": 0.3,
                "type": "column",
                "color": "#000000",
                //"fillColors": "#c0c0c0",
                //"dashLength":5,
                //"lineThickness" : 8,
                "title": "Aerogenerador 4",
                "valueField": "WTG04"

            },{
                "balloonText": "Disponibilidad [[title]] : <b>[[value]] %</b>",
                //"fillAlphas": 0.4,
                "fillAlphas": 0.9,
                "lineAlpha": 0.3,
                "type": "column",
                "color": "#000000",
                //"fillColors": "#c0c0c0",
                //"dashLength":5,
                //"lineThickness" : 8,
                "title": "Aerogenerador 5",
                "valueField": "WTG05"

            },{
                //"balloonText": "Monto proyectado para [[category]]: <b>$ [[value]]</b>",
                //"fillAlphas": 0.4,
                "balloonText": "Promedio Planta: <b>[[value]]%</b>",
                "bullet":"square",
                "bulletAlpha":0.5,
                "bulletSize":4,
                "bulletBorderAlpha":0,
                "fillAlphas": 0,
                "lineAlpha": 1,
                "color": "#000000",
                "lineColor" : "#96ccf4",
                //"fillColors": "#c0c0c0",
                "dashLength":4,
                "lineThickness" : 3,
                "valueField": "total",
                "title": "Disponibilidad Planta",
                "type": "step",

            },{
                //"balloonText": "Monto proyectado para [[category]]: <b>$ [[value]]</b>",
                //"fillAlphas": 0.4,
                "fillAlphas": 0,
                "lineAlpha": 0.8,
                "color": "#000000",
                "lineColor" : "#000000",
                //"fillColors": "#c0c0c0",
                //"dashLength":2,
                "lineThickness" : 4,
                "valueField": "meta",
                "title": "Disponibilidad Contractual",
                "type": "step",

            }],
            "categoryField": "date",
        });

        $('#chart_1').closest('.portlet').find('.fullscreen').click(function() {
            chart.invalidateSize();
        });
    }


    return {
        //main function to initiate the module
    	init: function(data){
    		data_chart_1=data[0];

    	},
        show: function() {
            initChart1();

        }
    };
}();