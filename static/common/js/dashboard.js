var Dashboard = function() {
    return {

        initDashboardDaterange: function(fecha_inicial,semana_str,fecha_inicio) {
            if (!jQuery().datetimepicker) {
                return;
            }
            moment.locale('es', {
                week: { dow: 1 } // Monday is the first day of the week
            });

            $('#dashboard-fecha').datetimepicker({
                format: 'DD-MM-YYYY',
                locale: 'es',
                defaultDate: fecha_inicial,
                maxDate: moment().endOf('day'),
                widgetParent: "#dashboard",
                minDate: fecha_inicio.startOf('isoweek'),
            });

            $('#dashboard-fecha').on('dp.change', function (e) {
                var fecha = $('#dashboard-fecha').data("DateTimePicker").date();
                var week = fecha.isoWeek();

                if (fecha){
                    var week_str = 'Semana '+week;
                    $("#dashboard-show").val(week_str);
                    if (week_str != semana_str){
                        console.log('Cambio semana!');
                        var week_msg = fecha.year() + '-' + week;
                        //console.log(week_msg);
                        $('#inputSemana').val(week_msg);
                        $('#formSemana').submit();
                    }
                };
            });

            $('#dashboard-fecha').on('dp.show', function (e) {
                console.log('show');
            });

            if (fecha_inicial) {
                $('#dashboard-fecha').data("DateTimePicker").date(fecha_inicial);
                $("#dashboard-show").val(semana_str);
            }
            $('#dashboard-opener').click(function(){
                $('#dashboard-fecha').data("DateTimePicker").toggle();
            });

        },
        initCounters: function() {
            var options = {
                useEasing: true,
                useGrouping: true,
                separator: '.',
                decimal: ',',
            };
            $("[name='counter']").each(function(){
                valor = $(this).attr('data-value');
                console.log(valor);
                var res = valor.split(",");
                if (res.length > 1) {
                    aux = parseFloat(res[0]+'.'+res[1]);
                    var demo = new CountUp(this, 0, aux, 1, 1.5, options);
                } else {
                    aux = parseInt(valor)
                    var demo = new CountUp(this, 0, valor, 0, 1.5, options);
                }

                if (!demo.error) {
                    demo.start();
                } else {
                    console.error(demo.error);
                }
            });

        },

        init: function(fecha,semana_str,fecha_inicial) {
            this.initDashboardDaterange(fecha,semana_str,fecha_inicial);
            this.initCounters();

        }
    }
}();
