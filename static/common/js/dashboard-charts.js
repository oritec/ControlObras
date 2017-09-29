var DashboardGraficos = function () {
     var GraficoColumnas = function (data,titulo,div) {
        $(div).highcharts({
            chart : {
                type: 'column'
            },
            title: {
                text: titulo,
                x: -20 //center
            },
            xAxis: {
                type: 'category'
            },
            yAxis: {
                title: {
                    text: 'Nº de componentes'
                }
            },
            plotOptions: {
                series: {
                    borderWidth: 0,
                    dataLabels: {
                        enabled: true,
                        format: '{point.y}'
                    }
                }
            },
            colors: ['#d6d6d6',
                     '#446e90',
                     '#f5e140',
                     '#189027',
                     '#FFF00B',
                     '#d14ef4',
                     '#434348',
                     '#8085e9',
                     '#f15c80',
                     '#91e8e1'],
            legend: {
                enabled:true,
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom',
                borderWidth: 0
            },
            series: data
        });
    }

    var GraficoLineas = function (data,titulo,div,thisweek) {
        $(div).highcharts({

            title: {
                text: titulo,
                x: -20 //center
            },
            xAxis: {
                type: 'category',
                labels: {
                    formatter: function () {
                        if (thisweek === this.value) {
                            return '<span style="fill: blue;font-weight: bold;">' + this.value + '</span>';
                        } else {
                            return this.value;
                        };
                    }
                }
            },
            yAxis: {
                title: {
                    text: 'Nº Aerogeneradores montados'
                }
            },
            plotOptions: {
                series: {
                    borderWidth: 0,
                    dataLabels: {
                        enabled: true,
                        format: '{point.y}',
                        style: {
                            fontSize: "8px"
                        }
                    }
                },
                line: {
                    marker: {
                        enabled: false
                    }
                }
            },
            tooltip: {
                crosshairs: true,
                shared: true
            },
            colors: ['#0855b7',
                     '#ffe760',
                     '#189027',
                     '#189027',
                     '#edb541',
                     '#bdb7bf',
                     '#d14ef4',
                     '#434348',
                     '#8085e9',
                     '#f15c80',
                     '#91e8e1'],
            legend: {
                enabled:true,
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom',
                borderWidth: 0
            },
            series: data
        });
    }

    return {
        //main function to initiate the module
        showGraficoColumnas: function(data,titulo,div) {
            //dataSeveridad = data;
            GraficoColumnas(data,titulo,div);
        },

        showGraficosLinea: function(data,titulo,div,thisweek) {
            GraficoLineas(data,titulo,div,thisweek);
        }
    };
}();