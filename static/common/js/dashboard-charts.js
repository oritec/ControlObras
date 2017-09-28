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
            colors: ['#bdb7bf',
                     '#0855b7',
                     '#edb541',
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

    return {
        //main function to initiate the module
        showGraficoColumnas: function(data,titulo,div) {
            //dataSeveridad = data;
            GraficoColumnas(data,titulo,div)
        }
    };
}();