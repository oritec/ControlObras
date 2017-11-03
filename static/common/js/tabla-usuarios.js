var TableDatatablesManaged = function () {

    var initTable1 = function () {

        var table = $('#tabla-usuarios');

        // begin first table
        table.dataTable({

            // Internationalisation. For more info refer to http://datatables.net/manual/i18n
            "language": {
                "lengthMenu": " _MENU_ &nbsp resultados",
                "search" : "Buscar: ",
            	"emptyTable":     "No hay datos en esta tabla",
                "info":           "Mostrando _START_ a _END_ de _TOTAL_ resultados",
                "infoEmpty":      "Mostrando 0 a 0 de 0 resultados",
                "infoFiltered":   "(Filtrando desde _MAX_ en total)",
                "infoPostFix":    "",
                "thousands":      ",",
                "loadingRecords": "Cargando...",
                "processing":     "�Procesando...",
                "zeroRecords":    "No se encontraron resultados",
                "paginate": {
                    "first":      "Primera",
                    "last":       "Ultima",
                    "next":       "Siguiente",
                    "previous":   "Previa"
                },
                "aria": {
                    "sortAscending":  ": activar para ordenar la columna ascendentemente",
                    "sortDescending": ": activar para ordenar la columna descendentemente"
                }
            },

            // Or you can use remote translation file
            //"language": {
            //   url: '//cdn.datatables.net/plug-ins/3cfcc339e89/i18n/Portuguese.json'
            //},

            // Uncomment below line("dom" parameter) to fix the dropdown overflow issue in the datatable cells. The default datatable layout
            // setup uses scrollable div(table-scrollable) with overflow:auto to enable vertical scroll(see: assets/global/plugins/datatables/plugins/bootstrap/dataTables.bootstrap.js). 
            // So when dropdowns used the scrollable div should be removed. 
            //"dom": "<'row'<'col-md-6 col-sm-12'l><'col-md-6 col-sm-12'f>r>t<'row'<'col-md-5 col-sm-12'i><'col-md-7 col-sm-12'p>>",

            "bStateSave": false, // save datatable state(pagination, sort, etc) in cookie.

            "lengthMenu": [
                [5, 15, 20, -1],
                [5, 15, 20, "All"] // change per page values here
            ],

            // set the initial value
            "pageLength": 20,
            "pagingType": "bootstrap_full_number",
            "columnDefs": [
                {  // set default column settings
                    'orderable': true,
                    'targets': [0,1]
                },
                {  // set default column settings
                    'orderable': false,
                    'targets': [2,3]
                },
                {
                    "searchable": true,
                    "targets": [0,1,2]
                },
                {
                    "className": "dt-center",
                    "targets": "_all"
                }
            ],

            "order": [
                [0, "asc"]
            ], // set first column as a default sort by asc


        });

        var tableWrapper = jQuery('#tabla-usuarios_wrapper');

    }


    return {

        //main function to initiate the module
        init: function () {
            if (!jQuery().dataTable) {
                return;
            }

            initTable1();
        }

    };

}();

jQuery(document).ready(function() {
    TableDatatablesManaged.init();
});
