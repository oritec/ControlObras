var TableDatatablesEditable = function () {
    var url2ask = '';
    var handleTable = function () {

        function restoreRow(oTable, nRow) {
            var aData = oTable.fnGetData(nRow);
            var jqTds = $('>td', nRow);

            for (var i = 0, iLen = jqTds.length; i < iLen; i++) {
                oTable.fnUpdate(aData[i], nRow, i, false);
            }

            oTable.fnDraw();
        }

        function editRow(oTable, nRow) {
            var aData = oTable.fnGetData(nRow);
            var jqTds = $('>td', nRow);

            jqTds[0].innerHTML = '<input type="hidden" class="form-control input-small" value="' + aData[0] + '">'+aData[0];

            jqTds[1].innerHTML = '<input type="text" class="form-control input-small" value="' + aData[1] + '">';
            jqTds[2].innerHTML = '<a class="edit" href="">Guardar</a>';
            jqTds[3].innerHTML = '<a class="cancel" href="">Cancelar</a>';
        }

        function saveRow(oTable, nRow) {
            var jqInputs = $('input', nRow);
            oTable.fnUpdate(jqInputs[0].value, nRow, 0, false);
            oTable.fnUpdate(jqInputs[1].value, nRow, 1, false);
            oTable.fnUpdate('<a class="edit" href="">Editar</a>', nRow, 2, false);
            oTable.fnUpdate('<a class="delete" href="">Borrar</a>', nRow, 3, false);
            oTable.fnDraw();
        }

        function cancelEditRow(oTable, nRow) {
            var jqInputs = $('input', nRow);
            oTable.fnUpdate(jqInputs[0].value, nRow, 0, false);
            oTable.fnUpdate(jqInputs[1].value, nRow, 1, false);
            oTable.fnUpdate('<a class="edit" href="">Editar</a>', nRow, 2, false);
            oTable.fnDraw();
        }

        var table = $('#tabla_observadores');

        var oTable = table.dataTable({

            // Uncomment below line("dom" parameter) to fix the dropdown overflow issue in the datatable cells. The default datatable layout
            // setup uses scrollable div(table-scrollable) with overflow:auto to enable vertical scroll(see: assets/global/plugins/datatables/plugins/bootstrap/dataTables.bootstrap.js). 
            // So when dropdowns used the scrollable div should be removed. 
            //"dom": "<'row'<'col-md-6 col-sm-12'l><'col-md-6 col-sm-12'f>r>t<'row'<'col-md-5 col-sm-12'i><'col-md-7 col-sm-12'p>>",

            "lengthMenu": [
                [5, 15, 20, -1],
                [5, 15, 20, "All"] // change per page values here
            ],

            // Or you can use remote translation file
            //"language": {
            //   url: '//cdn.datatables.net/plug-ins/3cfcc339e89/i18n/Portuguese.json'
            //},
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

            // set the initial value
            "pageLength": 15,

            "columnDefs": [{ // set default column settings
                'orderable': true,
                'targets': [0]
            }, {
                "searchable": true,
                "targets": [0]
            }],
            "order": [
                [0, "asc"]
            ] // set first column as a default sort by asc
        });

        var tableWrapper = $("#tabla_observadores_wrapper");

        var nEditing = null;
        var nNew = false;

        $('#tabla_observadores_new').click(function (e) {
            e.preventDefault();

            if (nNew && nEditing) {
                if (confirm("Hay un elemento que no has guardado. Lo quieres guardar primero?")) {
                    saveRow(oTable, nEditing); // save
                    $(nEditing).find("td:first").html("Untitled");
                    nEditing = null;
                    nNew = false;

                } else {
                    oTable.fnDeleteRow(nEditing); // cancel
                    nEditing = null;
                    nNew = false;
                    return;
                }
            }

            if (nEditing){
                bootbox.alert("Existe un elemento en edición.")
                return;
            }

            var aiNew = oTable.fnAddData(['-', '','','']);
            var nRow = oTable.fnGetNodes(aiNew[0]);
            editRow(oTable, nRow);
            nEditing = nRow;
            nNew = true;
        });

        table.on('click', '.delete', function (e) {
            e.preventDefault();

            if (confirm("Are you sure to delete this row ?") == false) {
                return;
            }

            var nRow = $(this).parents('tr')[0];
            var jqInputs = $('input', nRow);
            var aData = oTable.fnGetData(nRow);
            console.log(aData[0]);
            $.ajax({
                url: url2ask,
                type: 'DELETE',
                //dataType: 'json',
                data: {
                    'id': aData[0],
                    'nombre': aData[1]
                }
            }).done(function (result) {
                console.log(result);
                console.log(result.id);

            });
            oTable.fnDeleteRow(nRow);

        });

        table.on('click', '.cancel', function (e) {
            e.preventDefault();
            if (nNew) {
                oTable.fnDeleteRow(nEditing);
                nEditing = null;
                nNew = false;
            } else {
                restoreRow(oTable, nEditing);
                nEditing = null;
            }
        });

        table.on('click', '.edit', function (e) {
            e.preventDefault();
            nNew = false;
            
            /* Get the row as a parent of the link that was clicked on */
            var nRow = $(this).parents('tr')[0];

            if (nEditing !== null && nEditing != nRow) {
                /* Currently editing - but not this row - restore the old before continuing to edit mode */
                restoreRow(oTable, nEditing);
                editRow(oTable, nRow);
                nEditing = nRow;
            } else if (nEditing == nRow && this.innerHTML == "Guardar") {
                /* Editing this row and want to save it */
                var jqInputs = $('input', nRow);
                //console.log(jqInputs[0])
                //console.log($(jqInputs[0]))
                if (jqInputs[0].value == '-'){
                    var metodo = 'PUT';
                } else{
                    var metodo = 'POST';
                }
                //console.log(url2ask);
                $.ajax({
                    url: url2ask,
                    type: metodo,
                    dataType: 'json',
                    data: {
                        'id': jqInputs[0].value,
                        'nombre': jqInputs[1].value
                    }
                }).done(function (result) {
                    //console.log(result);
                    //console.log(result.id);
                    $(jqInputs[0]).val(result.id);
                    //jqInputs[0].value = result.id;
                    saveRow(oTable, nEditing);
                    nEditing = null;
                });


            } else {
                /* No edit in progress - let's start one */
                editRow(oTable, nRow);
                nEditing = nRow;
            }
        });
    }

    return {

        //main function to initiate the module
        init: function (url) {
            url2ask = url;
            handleTable();
        }

    };

}();

