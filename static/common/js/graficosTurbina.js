var GraficosPotencia = function() {
	var data_chart_1=[];
	var data_chart_2=[];
	var data_chart_3=[];
	var data_chart_4=[];
	var data_chart_5=[];
	var initChart1 = function() {
    	var chart = AmCharts.makeChart("chart_1", {
            "type": "xy",
            "theme": "light",
            "pathToImages": "static/common/assets/global/plugins/amcharts/amcharts/images/",

            "fontFamily": 'Open Sans',
            "color":    '#888',
            'colors':["#4b87ff", "#FF6600", "#FF9E01", "#008496", "#F8FF01",
                      "#B0DE09", "#04D215", "#0D8ECF", "#0D52D1", "#2A0CD0",
                      "#8A0CCF", "#CD0D74", "#754DEB", "#DDDDDD", "#999999",
                      "#333333", "#000000", "#57032A", "#CA9726", "#990000", "#4B0C25"],


            "dataProvider": data_chart_1,

            "zoomOutOnDataUpdate" : false,
            "export": {
                "enabled": true
             },

            "graphs": [{
                //"balloonText": "Monto proyectado para [[category]]: <b>$ [[value]]</b>",
                //"fillAlphas": 0.4,
                "lineAlpha": 1,
                "type": "smoothedLine",
                "xField": "v",
                "yField": "p",
                "lineColor" : "#0033cc",
                //"fillColors": "#c0c0c0",
                //"dashLength":5,
                "lineThickness" : 8,

            },{
                //"balloonText": "Monto proyectado para [[category]]: <b>$ [[value]]</b>",
                //"fillAlphas": 0.4,
                "lineAlpha": 0,
                "bullet": "round",
                "xField": "vx",
                "yField": "px",
                "lineColor": "#00cc00",
                "fillAlphas": 0,
                "bulletSize" :5,
                //"fillColors": "#c0c0c0",
                //"dashLength":5,
                //"lineThickness" : 2,

            }],
            "valueAxes": [{
                "position": "bottom",
                "axisAlpha": 0.5,
                "dashLength": 1,
                "title": "Velocidad del Viento [m/s]",
                "minimum":1.5,
                "maximum":16,
            }, {
                "axisAlpha": 0.5,
                "dashLength": 1,
                "position": "left",
                "title": "Potencia [kW]"
            }]
        });

        $('#chart_1').closest('.portlet').find('.fullscreen').click(function() {
            chart.invalidateSize();
        });
    }

    var initChart2 = function() {
    	var chart = AmCharts.makeChart("chart_2", {
            "type": "xy",
            "theme": "light",
            "pathToImages": "static/common/assets/global/plugins/amcharts/amcharts/images/",

            "fontFamily": 'Open Sans',
            "color":    '#888',
            'colors':["#4b87ff", "#FF6600", "#FF9E01", "#008496", "#F8FF01",
                      "#B0DE09", "#04D215", "#0D8ECF", "#0D52D1", "#2A0CD0",
                      "#8A0CCF", "#CD0D74", "#754DEB", "#DDDDDD", "#999999",
                      "#333333", "#000000", "#57032A", "#CA9726", "#990000", "#4B0C25"],


            "dataProvider": data_chart_2,

            "graphs": [{
                //"balloonText": "Monto proyectado para [[category]]: <b>$ [[value]]</b>",
                //"fillAlphas": 0.4,
                "lineAlpha": 1,
                "type": "smoothedLine",
                "xField": "v",
                "yField": "p",
                "lineColor" : "#0033cc",
                //"fillColors": "#c0c0c0",
                //"dashLength":5,
                "lineThickness" : 8,

            },{
                //"balloonText": "Monto proyectado para [[category]]: <b>$ [[value]]</b>",
                //"fillAlphas": 0.4,
                "lineAlpha": 0,
                "bullet": "round",
                "xField": "vx",
                "yField": "px",
                "lineColor": "#00cc00",
                "fillAlphas": 0,
                "bulletSize" :5,
                //"fillColors": "#c0c0c0",
                //"dashLength":5,
                //"lineThickness" : 2,

            }],
            "valueAxes": [{
                "position": "bottom",
                "axisAlpha": 0.5,
                "dashLength": 1,
                "title": "Velocidad del Viento [m/s]",
                "minimum":1.5,
                "maximum":16,
            }, {
                "axisAlpha": 0.5,
                "dashLength": 1,
                "position": "left",
                "title": "Potencia [kW]"
            }]
        });

        $('#chart_2').closest('.portlet').find('.fullscreen').click(function() {
            chart.invalidateSize();
        });
    }

    var initChart3 = function() {
    	var chart = AmCharts.makeChart("chart_3", {
            "type": "xy",
            "theme": "light",
            "pathToImages": "static/common/assets/global/plugins/amcharts/amcharts/images/",

            "fontFamily": 'Open Sans',
            "color":    '#888',
            'colors':["#4b87ff", "#FF6600", "#FF9E01", "#008496", "#F8FF01",
                      "#B0DE09", "#04D215", "#0D8ECF", "#0D52D1", "#2A0CD0",
                      "#8A0CCF", "#CD0D74", "#754DEB", "#DDDDDD", "#999999",
                      "#333333", "#000000", "#57032A", "#CA9726", "#990000", "#4B0C25"],


            "dataProvider": data_chart_3,

            "graphs": [{
                //"balloonText": "Monto proyectado para [[category]]: <b>$ [[value]]</b>",
                //"fillAlphas": 0.4,
                "lineAlpha": 1,
                "type": "smoothedLine",
                "xField": "v",
                "yField": "p",
                "lineColor" : "#0033cc",
                //"fillColors": "#c0c0c0",
                //"dashLength":5,
                "lineThickness" : 8,

            },{
                //"balloonText": "Monto proyectado para [[category]]: <b>$ [[value]]</b>",
                //"fillAlphas": 0.4,
                "lineAlpha": 0,
                "bullet": "round",
                "xField": "vx",
                "yField": "px",
                "lineColor": "#00cc00",
                "fillAlphas": 0,
                "bulletSize" :5,
                //"fillColors": "#c0c0c0",
                //"dashLength":5,
                //"lineThickness" : 2,

            }],
            "valueAxes": [{
                "position": "bottom",
                "axisAlpha": 0.5,
                "dashLength": 1,
                "title": "Velocidad del Viento [m/s]",
                "minimum":1.5,
                "maximum":16,
            }, {
                "axisAlpha": 0.5,
                "dashLength": 1,
                "position": "left",
                "title": "Potencia [kW]"
            }]
        });

        $('#chart_3').closest('.portlet').find('.fullscreen').click(function() {
            chart.invalidateSize();
        });
    }

    var initChart4 = function() {
    	var chart = AmCharts.makeChart("chart_4", {
            "type": "xy",
            "theme": "light",
            "pathToImages": "static/common/assets/global/plugins/amcharts/amcharts/images/",

            "fontFamily": 'Open Sans',
            "color":    '#888',
            'colors':["#4b87ff", "#FF6600", "#FF9E01", "#008496", "#F8FF01",
                      "#B0DE09", "#04D215", "#0D8ECF", "#0D52D1", "#2A0CD0",
                      "#8A0CCF", "#CD0D74", "#754DEB", "#DDDDDD", "#999999",
                      "#333333", "#000000", "#57032A", "#CA9726", "#990000", "#4B0C25"],


            "dataProvider": data_chart_4,

            "graphs": [{
                //"balloonText": "Monto proyectado para [[category]]: <b>$ [[value]]</b>",
                //"fillAlphas": 0.4,
                "lineAlpha": 1,
                "type": "smoothedLine",
                "xField": "v",
                "yField": "p",
                "lineColor" : "#0033cc",
                //"fillColors": "#c0c0c0",
                //"dashLength":5,
                "lineThickness" : 8,

            },{
                //"balloonText": "Monto proyectado para [[category]]: <b>$ [[value]]</b>",
                //"fillAlphas": 0.4,
                "lineAlpha": 0,
                "bullet": "round",
                "xField": "vx",
                "yField": "px",
                "lineColor": "#00cc00",
                "fillAlphas": 0,
                "bulletSize" :5,
                //"fillColors": "#c0c0c0",
                //"dashLength":5,
                //"lineThickness" : 2,

            }],
            "valueAxes": [{
                "position": "bottom",
                "axisAlpha": 0.5,
                "dashLength": 1,
                "title": "Velocidad del Viento [m/s]",
                "minimum":1.5,
                "maximum":16,
            }, {
                "axisAlpha": 0.5,
                "dashLength": 1,
                "position": "left",
                "title": "Potencia [kW]"
            }]
        });

        $('#chart_4').closest('.portlet').find('.fullscreen').click(function() {
            chart.invalidateSize();
        });
    }

    var initChart5 = function() {
    	var chart = AmCharts.makeChart("chart_5", {
            "type": "xy",
            "theme": "light",
            "pathToImages": "static/common/assets/global/plugins/amcharts/amcharts/images/",

            "fontFamily": 'Open Sans',
            "color":    '#888',
            'colors':["#4b87ff", "#FF6600", "#FF9E01", "#008496", "#F8FF01",
                      "#B0DE09", "#04D215", "#0D8ECF", "#0D52D1", "#2A0CD0",
                      "#8A0CCF", "#CD0D74", "#754DEB", "#DDDDDD", "#999999",
                      "#333333", "#000000", "#57032A", "#CA9726", "#990000", "#4B0C25"],


            "dataProvider": data_chart_5,

            "graphs": [{
                //"balloonText": "Monto proyectado para [[category]]: <b>$ [[value]]</b>",
                //"fillAlphas": 0.4,
                "lineAlpha": 1,
                "type": "smoothedLine",
                "xField": "v",
                "yField": "p",
                "lineColor" : "#0033cc",
                //"fillColors": "#c0c0c0",
                //"dashLength":5,
                "lineThickness" : 8,

            },{
                //"balloonText": "Monto proyectado para [[category]]: <b>$ [[value]]</b>",
                //"fillAlphas": 0.4,
                "lineAlpha": 0,
                "bullet": "round",
                "xField": "vx",
                "yField": "px",
                "lineColor": "#00cc00",
                "fillAlphas": 0,
                "bulletSize" :5,
                //"fillColors": "#c0c0c0",
                //"dashLength":5,
                //"lineThickness" : 2,

            }],
            "valueAxes": [{
                "position": "bottom",
                "axisAlpha": 0.5,
                "dashLength": 1,
                "title": "Velocidad del Viento [m/s]",
                "minimum":1.5,
                "maximum":16,
            }, {
                "axisAlpha": 0.5,
                "dashLength": 1,
                "position": "left",
                "title": "Potencia [kW]"
            }]
        });

        $('#chart_5').closest('.portlet').find('.fullscreen').click(function() {
            chart.invalidateSize();
        });
    }


    return {
        //main function to initiate the module
    	init: function(data){
    		data_chart_1=data[0];
    		data_chart_2=data[1];
    		data_chart_3=data[2];
    		data_chart_4=data[3];
    		data_chart_5=data[4];
    	},
        show: function() {
            initChart1();
            initChart2();
            initChart3();
            initChart4();
            initChart5();
        }
    };
}();