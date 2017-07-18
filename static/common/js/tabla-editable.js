var TablaEditable = function () {

    var handleTable = function () {

        var table = $('#eventos');

        var oTable = table.dataTable({

            // Uncomment below line("dom" parameter) to fix the dropdown overflow issue in the datatable cells. The default datatable layout
            // setup uses scrollable div(table-scrollable) with overflow:auto to enable vertical scroll(see: assets/global/plugins/datatables/plugins/bootstrap/dataTables.bootstrap.js).
            // So when dropdowns used the scrollable div should be removed.
            //"dom": "<'row'<'col-md-6 col-sm-12'l><'col-md-6 col-sm-12'f>r>t<'row'<'col-md-5 col-sm-12'i><'col-md-7 col-sm-12'p>>",

            "lengthMenu": [
                [5, 15, 20, -1],
                [5, 15, 20, "Todas"] // change per page values here
            ],
            // set the initial value
            "pageLength": 15,

            //"bFilter": false,

            "language": {
                "lengthMenu": " _MENU_ &nbsp resultados",
                "search" : "Buscar: ",
            	"emptyTable":     "No hay datos en esta tabla",
                "info":           "Mostrando _START_ a _END_ de _TOTAL_ resultados",
                "infoEmpty":      "Mostrando 0 a 0 de 0 resultados",
                "infoFiltered":   "(Filtrando desde _MAX_ en total)",
                "infoPostFix":    "",
                "decimal":        ",",
                "thousands":      ".",
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
            "columnDefs": [{ // set default column settings
            	"orderDataType": "dom-text", "type": "string", // Truco para ordenar fecha con comentario
            	"targets": [0,1]
                },{
                "orderable": false,
                "targets": [8]
                }, {
                "orderable": true,
                "targets": [0,1,2,3,4,5,6,7]
                }
            ],
            "order": [
                [0, "desc"]
            ] // set first column as a default sort by asc
        });

        var tableWrapper = $("#datos_wrapper");

        tableWrapper.find(".dataTables_length select").select2({
            showSearchInput: true //hide search box with special css class
        }); // initialize select2 dropdown

        var nEditing = null;
        var nNew = false;

    }

    var handleTable2 = function () {

        var table = $('#listabusqueda');

        var oTable = table.dataTable({

            // Uncomment below line("dom" parameter) to fix the dropdown overflow issue in the datatable cells. The default datatable layout
            // setup uses scrollable div(table-scrollable) with overflow:auto to enable vertical scroll(see: assets/global/plugins/datatables/plugins/bootstrap/dataTables.bootstrap.js).
            // So when dropdowns used the scrollable div should be removed.
            //"dom": "<'row'<'col-md-6 col-sm-12'l><'col-md-6 col-sm-12'f>r>t<'row'<'col-md-5 col-sm-12'i><'col-md-7 col-sm-12'p>>",

            "lengthMenu": [
                [5, 15, 20, -1],
                [5, 15, 20, "Todas"] // change per page values here
            ],
            // set the initial value
            "pageLength": 15,

            //"bFilter": false,

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
            "columnDefs": [{ // set default column settings
            	"orderDataType": "dom-text", "type": "string", // Truco para ordenar fecha con comentario
            	"targets": [1,2]
                }, {
                "orderable": false,
                "targets": [5,6,7]
                }, {
                "orderable": true,
                "targets": [1,2,3,4]
                }
            ],
            "order": [
                [1, "desc"]
            ] // set first column as a default sort by asc
        });

        var tableWrapper = $("#datos-trayecto_wrapper");

        tableWrapper.find(".dataTables_length select").select2({
            showSearchInput: false //hide search box with special css class
        }); // initialize select2 dropdown

        var nEditing = null;
        var nNew = false;

    }

    var handleTable3 = function () {

        var table = $('#trayectos');

        var oTable = table.dataTable({

            // Uncomment below line("dom" parameter) to fix the dropdown overflow issue in the datatable cells. The default datatable layout
            // setup uses scrollable div(table-scrollable) with overflow:auto to enable vertical scroll(see: assets/global/plugins/datatables/plugins/bootstrap/dataTables.bootstrap.js).
            // So when dropdowns used the scrollable div should be removed.
            //"dom": "<'row'<'col-md-6 col-sm-12'l><'col-md-6 col-sm-12'f>r>t<'row'<'col-md-5 col-sm-12'i><'col-md-7 col-sm-12'p>>",

            "lengthMenu": [
                [5, 15, 20, -1],
                [5, 15, 20, "Todas"] // change per page values here
            ],
            // set the initial value
            "pageLength": 15,

            //"bFilter": false,

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
            "columnDefs": [{ // set default column settings
            	"orderDataType": "dom-text", "type": "string", // Truco para ordenar fecha con comentario
            	"targets": [1,2]
                },
                {
                "searchable": false,
                "targets": [-1]
                }, {
                "orderable": false,
                "targets": [-1]
                }
            ],
            "order": [
                [0, "desc"]
            ] // set first column as a default sort by asc
        });

        var tableWrapper = $("#trayectos_wrapper");

        tableWrapper.find(".dataTables_length select").select2({
            showSearchInput: false //hide search box with special css class
        }); // initialize select2 dropdown

        var nEditing = null;
        var nNew = false;

    }

    return {

        //main function to initiate the module
        init: function () {
            handleTable();
            handleTable2();
            handleTable3();
        }

    };

}();