var Dashboard = function() {
    return {

        initDashboardDaterange: function() {
            if (!jQuery().datetimepicker) {
                return;
            }
            moment.locale('es', {
                week: { dow: 1 } // Monday is the first day of the week
            });

            $('#dashboard-report-range').datetimepicker({
                format: 'DD-MM-YYYY',
                locale: 'es',
                defaultDate: moment(),
                maxDate: moment(),
            });

            $('#dashboard-report-range').on('dp.change', function (e) {
                var fecha = $('#dashboard-report-range').data("DateTimePicker").date();
                if( fecha ) {
                    var week = fecha.isoWeek();
                    $("#dashboard-input").val('Semana ' + week);
                } else {
                    fecha = moment()
                    var week = fecha.isoWeek();
                    $("#dashboard-input").val('Semana ' + week);
                };
            });

            $('#dashboard-report-range').on('dp.show', function (e) {
                var fecha = $('#dashboard-report-range').data("DateTimePicker").date();
                if( fecha ) {
                    var week = fecha.isoWeek();
                    $("#dashboard-input").val('Semana ' + week);
                } else {
                    fecha = moment()
                    var week = fecha.isoWeek();
                    $("#dashboard-input").val('Semana ' + week);
                };
            });


            var fecha = $('#dashboard-report-range').data("DateTimePicker").date();
            if( fecha ) {
                var week = fecha.isoWeek();
                $("#dashboard-input").val('Semana ' + week);
            } else {
                fecha = moment()
                var week = fecha.isoWeek();
                $("#dashboard-input").val('Semana ' + week);
            };

        },

        init: function() {
            this.initDashboardDaterange();
        }
    }
}();


jQuery(document).ready(function() {
    Dashboard.init(); // init metronic core componets
});