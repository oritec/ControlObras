var NCRGraficos = function () {

    var GraficoEstado = function (data) {
        $('#grafico_estado').highcharts({
            chart : {
                type: 'pie',
                options3d: {
                    enabled: true,
                    alpha: 45,
                    beta: 0
                }
            },
            title: {
                text: 'Número de observaciones por estado',
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
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    depth: 35,
                    dataLabels: {
                        enabled: true,
                        format: '{y}',
                        connectorPadding:0,
                        connectorWidth: 1,
                        distance:10
                    },
                    showInLegend: true
                }
            },
            legend: {
                enabled:true,
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom',
                borderWidth: 0
            },
            series: [{
                type: 'pie',
                name: 'Nº de observaciones',
                data: data,
            }]
        });
    }

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
                    text: 'Nº de observaciones'
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
            legend: {
                enabled:true,
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom',
                borderWidth: 0
            },
            series: [{
                name: 'Nº de observaciones',
                data: data
            }]
        });
    }

    var GraficoFull = function (data1,data2,titulo,div) {
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
            colors: ['#52CFFF',
                     '#f7a35c',
                     '#2ced7e',
                     '#FFF00B',
                     '#d14ef4',
                     '#434348',
                     '#8085e9',
                     '#f15c80',
                     '#2b908f',
                     '#91e8e1'],
            plotOptions: {
                series: {
                    borderWidth: 0,
                    dataLabels: {
                        enabled: true,
                        format: '{point.y}'
                    }
                }
            },
            legend: {
                enabled:true,
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom',
                borderWidth: 0
            },
            series: data1
        });
    }

    var GraficoFull2 = function (data1,titulo,div) {
        $(div).highcharts({
            chart : {
                type: 'column'
            },
            title: {
                text: titulo,
                x: -20 //center
            },
            xAxis: {
                type: 'category',
                labels: {
                    style: {
                        fontSize: '7px'
                    }
                }
            },
            yAxis: {
                title: {
                    text: 'Nº de observaciones'
                }
            },
            colors: ['#52CFFF',
                     '#f7a35c',
                     '#2ced7e',
                     '#FFF00B',
                     '#d14ef4',
                     '#434348',
                     '#8085e9',
                     '#f15c80',
                     '#2b908f',
                     '#91e8e1'],
            plotOptions: {
                series: {
                    borderWidth: 0,
                    dataLabels: {
                        enabled: true,
                        format: '{point.y}'
                    }
                },
                column: {
                    stacking: 'normal'
                }
            },
            legend: {
                enabled:true,
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom',
                borderWidth: 0
            },
            series: data1
        });
    }

    var GraficoFull3 = function (data1,data2,titulo,div) {
        $(div).highcharts({
            chart : {
                type: 'bar'
            },
            title: {
                text: titulo,
                x: -20 //center
            },
            xAxis: {
                type: 'category'
            },
            colors: ['#52CFFF',
                     '#f7a35c',
                     '#2ced7e',
                     '#FFF00B',
                     '#d14ef4',
                     '#434348',
                     '#8085e9',
                     '#f15c80',
                     '#2b908f',
                     '#91e8e1'],
            plotOptions: {
                series: {
                    borderWidth: 0,
                    dataLabels: {
                        enabled: true,
                        format: '{point.y}'
                    }
                }
            },
            legend: {
                enabled:true,
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom',
                borderWidth: 0
            },
            series: data1
        });
    }

    var GraficoFull4 = function (data1,data2,titulo,div) {
        $(div).highcharts({
            chart : {
                type: 'bar'
            },
            title: {
                text: titulo,
                x: -20 //center
            },
            xAxis: {
                type: 'category'
            },
            colors: ['#52CFFF',
                     '#f7a35c',
                     '#2ced7e',
                     '#FFF00B',
                     '#d14ef4',
                     '#434348',
                     '#8085e9',
                     '#f15c80',
                     '#2b908f',
                     '#91e8e1'],
            plotOptions: {
                series: {
                    borderWidth: 0,
                    dataLabels: {
                        enabled: true,
                        format: '{point.y}'
                    },
                    stacking: 'normal'
                }
            },
            legend: {
                enabled:true,
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom',
                borderWidth: 0
            },
            series: data1
        });
    }

    return {
        //main function to initiate the module
        showGraficoEstado: function (data) {
            //dataEstado = data;
            GraficoEstado(data);
        },
        showGraficoColumnas: function(data,titulo,div) {
            //dataSeveridad = data;
            GraficoColumnas(data,titulo,div)
        },
        showGraficoFull: function(data1,data2,titulo,div) {
            //dataSeveridad = data;
            GraficoFull(data1,data2,titulo,div)
        },
        showGraficoFull2: function(data,titulo,div) {
            //dataSeveridad = data;
            GraficoFull2(data,titulo,div)
        },
        showGraficoFull3: function(data1,data2,titulo,div) {
            //dataSeveridad = data;
            GraficoFull3(data1,data2,titulo,div)
        },
        showGraficoFull4: function(data1,data2,titulo,div) {
            //dataSeveridad = data;
            GraficoFull4(data1,data2,titulo,div)
        }
    };
}();