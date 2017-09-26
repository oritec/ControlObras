var FUGraficos = function () {

    var GraficoPlanificacion = function (data,xlabels,ylabels,titulo,div,thisweek) {
        $('#'+div).highcharts({
            chart: {
                type: 'heatmap',
                marginTop: 40,
                marginBottom: 80,
                plotBorderWidth: 1
            },
            title: {
                text: titulo,
                x: -20 //center
            },

            colors: ['#1ce67b',
                     '#fff110',
                     '#ff6559',
                     '#7cb5ec',
                     '#434348',
                     '#f7a35c',
                     '#8085e9',
                     '#f15c80',
                     '#2b908f',
                     '#91e8e1'],

            xAxis: {
                categories: xlabels,
                labels: {
                    formatter: function () {
                        if (thisweek === this.value) {
                            return '<span style="fill: blue;font-weight: bold;">' + this.value + '</span>';
                        } else {
                            return this.value;
                        };
                    }
                },
            },

            yAxis: {
                categories: ylabels,
                title: null
            },

            colorAxis: {
                min: 0,
                minColor: '#FFFFFF',
                maxColor: Highcharts.getOptions().colors[0]
            },

            legend: {
                enabled:false,
            },

            tooltip: {
                formatter: function () {
                    return 'Semana: ' + this.series.xAxis.categories[this.point.x] +
                        ', Componente: ' + this.series.yAxis.categories[this.point.y];
                }
            },

            series: [{
                name: 'Descargas',
                borderWidth: 1,
                data: data,
                dataLabels: {
                    enabled: true,
                    color: '#000000'
                }
            }]
        });
    }


    return {
        //main function to initiate the module
        showGraficoPlanificacion: function (xlabels,ylabels,data,titulo,div,thisweek) {
            //dataEstado = data;
            GraficoPlanificacion(data,xlabels,ylabels,titulo,div,thisweek);
        }
    };
}();