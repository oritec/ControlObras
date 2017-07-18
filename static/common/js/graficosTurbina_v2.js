var GraficosPotencia = function() {
	var data_chart_1=[];
	var data_teorica=[];

	var initChart1 = function() {
    	var chart = Highcharts.chart('chart_1', {
            chart: {
                type: 'scatter',
                zoomType: 'xy'
            },
            boost: {
                useGPUTranslations: true,
                usePreAllocated: true
            },
            xAxis: {
                min: 0,
                max: 16,
                gridLineWidth: 1,
                title:{
                    text:'Velocidad del viento [m/s]',
                }
            },

            yAxis: {
                // Renders faster when we don't have to compute min and max
                min: 0,
                max: 3500,
                minPadding: 0,
                maxPadding: 0,
                title:{
                    text:'Potencia [kW]',
                }
            },
            legend:{
                enabled: false,
            },
            title:{
                text:'',
            },
            series: [{
                boostBlending: 'alpha',
                enableMouseTracking: false,
                name: 'Power',
                color: '#00cc00',
                data:  data_chart_1,
                tooltip: {
                    followPointer: false,
                    pointFormat: '[{point.x:.1f}, {point.y:.1f}]'
                },
                marker:{
                    radius : 2,
                }
            },{
                type:'line',
                boostBlending: 'alpha',
                enableMouseTracking: false,
                name: 'Teorico',
                color: '#0033cc',
                data:  data_teorica,
                tooltip: {
                    followPointer: false,
                    pointFormat: '[{point.x:.1f}, {point.y:.1f}]'
                },
                marker:{
                    radius : 2,
                },
                dashStyle: "Solid",
                lineWidth: 6,

            }]
        });

        $('#chart_1').closest('.portlet').find('.fullscreen').click(function() {
            chart.invalidateSize();
        });
    }

    return {
        //main function to initiate the module
    	init: function(data){
    		data_chart_1=data[0];
    		data_teorica=data[1];
    	},
        show: function() {
            initChart1();
        }
    };
}();