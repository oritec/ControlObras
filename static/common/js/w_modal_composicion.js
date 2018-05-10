$( document ).ready(function() {

    $('#composicion').on('show.bs.modal', function (e) {
        console.log('show modal composicion');
        if (typeof e.relatedTarget != "undefined") {
            $("#composicion_pie").val('');
            var select_val = $('#composicion_nofotos').val();
            console.log(select_val);
            if ( select_val != null){
                showPhotoGrid(select_val,'1');
            }
            for (var i = 0; i < 6; i++) {
                $(".preview_" + (i + 1).toString()).each(function (index) {
                    $(this).empty();
                });
            }
            $("#edit_composicion").val('0');
        } else{
            var select_val = $('#composicion_nofotos').val();
            var pattern_id = $('#pattern_img_id').val();
            console.log(select_val);
            if ( select_val != null){
                showPhotoGrid(select_val, pattern_id);
            }
        }

    })

    function showPhotoGrid(idx, pattern_id){
        console.log('showPhotoGrid');
        $(".composicion_row").each(function( ) {
            //console.log($(this));
            $(this).hide();
        });
        console.log(idx);
        $('#composicion_row_'+idx).show();
        var img_selected = $('#img-' + idx + '-' + pattern_id);
        console.log(img_selected);
        manageBtnRadio(img_selected.siblings('.btn'));
    }

    $('#composicion_nofotos').on('changed.bs.select', function (e) {
        var select_val = $('#composicion_nofotos').val();
        //console.log(select_val);
        //showPhotoGrid(
        if ( select_val != null){
            showPhotoGrid(select_val,'1');
        }
    });

    $('#composicion').modalSteps({
        btnCancelHtml: 'Cancelar',
        btnPreviousHtml: 'Anterior',
        btnNextHtml: 'Siguiente',
        btnLastStepHtml: 'Guardar',
        disableNextButton: false,
        completeCallback: function(){
            //console.log('Enviando');
            $("#formComposicion").submit();
        },
        callbacks: {
            '2': modalChange_step2
        }
    });

    function modalChange_step2(){
        //console.log('Step2');
        var el = $('input[id^="img-"]:checked').siblings('.btn');
        $("#pattern").val(el.text());
        $("div[id^=\"row_img\"]").each(function( ) {
            $(this).hide();
        });
        //$(".fileinput").each(function(){
        //    $(this).fileinput('clear');
        //});

        $('#row_img_'+el.text()).show();
        //row_img_1V3H

    }

    function manageBtnRadio(el){
        var elemento = $(el);
        $('.btn-radio').not(elemento).removeClass('active')
    		.siblings('input').prop('checked',false)
            .siblings('.img-radio').css('opacity','0.5');
    	$(el).addClass('active')
            .siblings('input').prop('checked',true)
    		.siblings('.img-radio').css('opacity','1');
    }

    $('.btn-radio').click(function(e) {
        manageBtnRadio(this);
    });

    $('.img-radio').click(function(e) {
        manageBtnRadio($(this).siblings('.btn'));
    });

    $('.add_composicion').click(function( e) {
        var act_id = $(this).attr("act_id");
        $("#act_id").val(act_id);

    });
    //$('#file_input_1').fileinput();
});