function clearOptions(){
    for (var i = 2; i < 6; i++) {
        //console.log($("[nombre='estadofu'] ,[value="+options[i]+"]"));
        $("[nombre=estadofu] ,[value="+i.toString()+"]").prop('checked', false);
    }
}

function addComponente(url){
    var selector = $("#id_componente");
    selector.select2({
        dropdownParent: $('#basic')
    });
    if (selector.hasClass("select2-hidden-accessible")) {
        console.log('initialized');
        console.log(url);
        selector.val('').trigger('change');
        clearOptions();
        selector.on('change.select2', function (e) {
            var data = selector.select2('data');
            console.log(data);
            console.log(data[0].id);
            clearOptions();
            $.ajax({
                type: "post",
                url: url,
                data: {"id": data[0].id, "parque_slug": ""},
                success: function (data) {
                    console.log(data);
                    for (var i = 0; i < data.length; i++) {
                        console.log($("[nombre='estadofu'] ,[value="+data[i]+"]"));
                        $("[nombre=estadofu] ,[value="+data[i]+"]").prop('checked', true);
                    }
                    },
                error: function (jqXhr, textStatus, errorThrown) {
                    console.log(errorThrown);
                }
            })
        });
    }

}

function cancelComponente(){
    console.log('del selector');
    var selector = $("#id_componente");
    // Destroy Select2
    selector.select2('destroy');

    // Unbind the event
    selector.off('select2:select');
}