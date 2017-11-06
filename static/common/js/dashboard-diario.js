var Dashboard = function() {
    return {

        initDashboardDaterange: function(fecha_inicial,semana_str,fecha_inicio) {
            if (!jQuery().datetimepicker) {
                return;
            }
            moment.locale('es', {
                week: { dow: 1 } // Monday is the first day of the week
            });

            $('#dashboard').datetimepicker({
                format: 'DD-MM-YYYY',
                locale: 'es',
                defaultDate: fecha_inicial,
                maxDate: moment().endOf('day'),
                minDate: fecha_inicio.startOf('isoweek'),
                ignoreReadonly: true,
            });

            $('#dashboard').on('dp.change', function (e) {
                var fecha = $('#dashboard').data("DateTimePicker").date();

                if (fecha){
                    console.log(fecha.format('DD-MM-YYYY'));
                    $('#inputFecha').val(fecha.format('DD-MM-YYYY'));
                    $('#formFecha').submit();
                }
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
