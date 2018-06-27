$(function() {
    $('[data-action="agregar"]').click(function() {
        //console.log('boton agregar');
        //console.log($(this).attr('data-target'));
        var elemento = $(this).attr('data-target');
        $('#titulo_agregar').html('Agregar '+ elemento);
        $('#agregar_form_target').val(elemento);
        $('#agregar').modal('show');
    });
    $('[data-action="editar"]').click(function() {
        //console.log('boton editar');
        //console.log();
        var elemento = $(this).attr('data-target');
        var id = $(this).attr('data-id');
        $('#titulo_editar').html('Editar '+ elemento);
        $('#editar_form_nombre').val($(this).siblings('div').text().trim());
        $('#editar_form_id').val(id);
        $('#editar_form_target').val(elemento);
        $('#editar').modal('show');
    });

    $('[data-action="eliminar"]').click(function() {
        //console.log('boton editar');
        //console.log();
        var elemento = $(this).attr('data-target');
        var id = $(this).attr('data-id');
        //$('#titulo_editar').html('Editar '+ elemento);
        //$('#editar_form_nombre').val($(this).siblings('div').text().trim());
        $('#eliminar_form_id').val(id);
        $('#eliminar_form_target').val(elemento);
        $('#eliminar').modal('show');
    });

    $('.nestable').each(function() {
        $(this).nestable({
            group: 0,       // you can change this name as you like
            maxDepth: 1,    // Si se pueden anidar en niveles. 1: no hay anidacion.
            callback: function (l, e) {
                // l is the main container
                // e is the element that was moved
                console.log('callback nestable');
                //console.log(l);
                //console.log(e);
                console.log($(l).nestable('serialize'));
                var url2ask = $(l).attr('data-url');
                var elemento = $(l).attr('data-target');
                console.log(elemento);
                $.ajax({
                    type: "post",
                    url: url2ask,
                    data: {
                        "target": elemento,
                        "orden": JSON.stringify($(l).nestable('serialize')),
                        "csrfmiddlewaretoken": document.getElementsByName('csrfmiddlewaretoken')[0].value
                    },
                    success: function (data) {
                        console.log('OK');
                    }
                });
            },
        })
    })

});