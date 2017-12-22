# -*- coding: utf-8 -*-
from django import forms
from ncr.models import Observacion, Revision,EstadoRevision,Severidad,Componente,Subcomponente,Tipo
from vista.models import ParqueSolar,Aerogenerador
from fu.models import ConfiguracionFU
import logging
from datetime import date
logger = logging.getLogger('oritec')

class ObservacionForm(forms.ModelForm):
    fecha_observacion = forms.DateField(widget=forms.DateInput(format = '%d-%m-%Y'),
                                 input_formats=('%d-%m-%Y',))
    class Meta:
        model = Observacion
        fields = ['parque','nombre','aerogenerador','fecha_observacion','componente','sub_componente','tipo',
                  'punchlist','reported_by','clase','no_serie']
        labels = {
            'nombre': 'Descripción',
            'reported_by': 'Reportado por',
            'no_serie': 'Número de Serie',
            'clase': 'Categoría',
            'fecha_observacion': 'Fecha observación'
        }
    def __init__(self, *args, **kwargs):
        super(ObservacionForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            parque = kwargs['initial']['parque']
            self.fields['aerogenerador'].queryset = Aerogenerador.objects.filter(parque=parque)
        elif 'instance' in kwargs:
            parque = kwargs['instance'].parque
            self.fields['aerogenerador'].queryset = Aerogenerador.objects.filter(parque=parque)
        #parque = kwargs['initial']['parque']
        #opciones = []
        #for ag in range(1,parque.no_aerogeneradores+1):
            #logger.debug(ag)
        #    opciones.append((ag,'WTG'+str(ag).zfill(2)))
        #self.fields['aerogenerador'] = forms.ChoiceField(
        #    choices=opciones
        #)
        self.fields['parque'].widget = forms.HiddenInput()
        self.fields['aerogenerador'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['aerogenerador'].widget.attrs['data-live-search'] = 'true'
        self.fields['aerogenerador'].widget.attrs['data-size'] = '8'
        self.fields['nombre'].widget.attrs['class'] = 'form-control'
        self.fields['aerogenerador'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['fecha_observacion'].widget.attrs['class'] = 'form-control'
        self.fields['fecha_observacion'].widget.attrs['readonly'] = True
        self.fields['componente'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['componente'].widget.attrs['data-live-search'] = 'true'
        self.fields['componente'].widget.attrs['data-size'] = '8'
        self.fields['sub_componente'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['sub_componente'].widget.attrs['data-live-search'] = 'true'
        self.fields['sub_componente'].widget.attrs['data-size'] = '8'
        self.fields['no_serie'].widget.attrs['class'] = 'form-control'
        self.fields['tipo'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['tipo'].widget.attrs['data-live-search'] = 'true'
        self.fields['tipo'].widget.attrs['data-size'] = '8'
        self.fields['punchlist'].widget.attrs['class'] = 'make-switch'
        self.fields['punchlist'].widget.attrs['data-size'] = 'small'
        self.fields['punchlist'].widget.attrs['data-on-text'] = 'Si'
        self.fields['punchlist'].widget.attrs['data-off-text'] = 'No'
        self.fields['punchlist'].widget.attrs['checked'] = ''
        self.fields['clase'].widget.attrs['class'] = 'make-switch'
        self.fields['clase'].widget.attrs['data-size'] = 'small'
        self.fields['clase'].widget.attrs['data-on-text'] = 'NCR'
        self.fields['clase'].widget.attrs['data-off-text'] = 'Incidencia'
        self.fields['reported_by'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['reported_by'].widget.attrs['data-live-search'] = 'true'
        self.fields['reported_by'].widget.attrs['data-size'] = '8'

class RevisionForm(forms.ModelForm):
    fecha_revision = forms.DateField(widget=forms.HiddenInput(),
                                        input_formats=('%d-%m-%Y',))
    class Meta:
        model = Revision
        fields = ['fecha_revision','severidad','prioridad','nombre','descripcion']
        labels = {
            'nombre': 'Descripción',
            'descripcion': 'Detalle',
        }
    def __init__(self, *args, **kwargs):
        super(RevisionForm, self).__init__(*args, **kwargs)
        #self.fields['fecha_revision'].widget = forms.HiddenInput()
        self.fields['severidad'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['severidad'].widget.attrs['data-live-search'] = 'true'
        self.fields['prioridad'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['prioridad'].widget.attrs['data-size'] = '8'
        self.fields['nombre'].widget.attrs['class'] = 'form-control'
        self.fields['descripcion'].widget = forms.Textarea()
        self.fields['descripcion'].widget.attrs['class'] = 'form-control'
        self.fields['descripcion'].widget.attrs['row'] = '3'

class RevisionFormFull(forms.ModelForm):
    fecha_revision = forms.DateField(widget=forms.DateInput(format = '%d-%m-%Y'),
                                 input_formats=('%d-%m-%Y',))
    class Meta:
        model = Revision
        fields = ['observacion','fecha_revision','severidad','prioridad','nombre','descripcion', 'estado','reported_by']
        labels = {
            'nombre': 'Descripción',
            'fecha_revision' : 'Fecha revisión',
            'descripcion': 'Detalle',
            'reported_by': 'Reportado por'
        }
    def __init__(self, *args, **kwargs):
        super(RevisionFormFull, self).__init__(*args, **kwargs)
        self.fields['observacion'].widget = forms.HiddenInput()
        self.fields['severidad'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['severidad'].widget.attrs['data-live-search'] = 'true'
        self.fields['severidad'].widget.attrs['data-size'] = '8'
        self.fields['prioridad'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['descripcion'].widget = forms.Textarea()
        self.fields['descripcion'].widget.attrs['class'] = 'form-control'
        self.fields['descripcion'].widget.attrs['row'] = '3'
        self.fields['fecha_revision'].widget.attrs['class'] = 'form-control'
        self.fields['estado'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['reported_by'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['reported_by'].widget.attrs['data-live-search'] = 'true'
        self.fields['reported_by'].widget.attrs['data-size'] = '8'
        self.fields['nombre'].widget.attrs['class'] = 'form-control'

class NCR(forms.Form):
    aerogenerador = forms.ModelMultipleChoiceField(queryset=Aerogenerador.objects.all(),required=False)
    condicion = forms.MultipleChoiceField(choices=[('reparadas', 'Cerrada'), ('no reparadas', 'Abierta')],required=False,label="Condición")
    estado = forms.ModelMultipleChoiceField(queryset=EstadoRevision.objects.all(),required=False)
    severidad = forms.ModelMultipleChoiceField(queryset=Severidad.objects.all(),required=False)
    componente = forms.ModelMultipleChoiceField(queryset=Componente.objects.all(),required=False)
    subcomponente = forms.ModelMultipleChoiceField(queryset=Subcomponente.objects.all(),required=False)
    tipo = forms.ModelMultipleChoiceField(queryset=Tipo.objects.all(),required=False)
    clase = forms.MultipleChoiceField(choices=[('1', 'NCR'), ('0', 'Incidencia')],
                                          required=False, label="Categoría")
    punchlist = forms.MultipleChoiceField(choices=[('0', 'No'), ('1', 'Si')],
                                          required=False, label="Punchlist")
    fecha_from = forms.DateField(widget=forms.DateInput(format='%d-%m-%Y'), input_formats=('%d-%m-%Y',), initial=date.today)
    fecha_to = forms.DateField(widget=forms.DateInput(format='%d-%m-%Y'), input_formats=('%d-%m-%Y',), initial=date.today)
    def __init__(self, *args, **kwargs):
        parque = kwargs.pop('parque')
        super(NCR, self).__init__(*args, **kwargs)
        try:
            obj = ConfiguracionFU.objects.get(parque=parque)
            self.fields['fecha_from'].initial = obj.fecha_inicio
        except ConfiguracionFU.DoesNotExist:
            logger.debug("ConfiguracionFU para parque no existe, queda todo igual")
        self.fields['aerogenerador'].queryset = Aerogenerador.objects.filter(parque=parque).order_by('idx')
        self.fields['fecha_from'].widget.attrs['class'] = 'form-control'
        self.fields['fecha_from'].widget.attrs['readonly'] = True
        self.fields['fecha_to'].widget.attrs['class'] = 'form-control'
        self.fields['fecha_to'].widget.attrs['readonly'] = True

#        self.fields['aerogenerador'].widget.attrs['class'] = 'form-control'

class Punchlist(forms.Form):
    aerogenerador = forms.ModelMultipleChoiceField(queryset=Aerogenerador.objects.all().order_by('idx'),required=False)
    fecha_from = forms.DateField(widget=forms.DateInput(format='%d-%m-%Y'), input_formats=('%d-%m-%Y',),
                                 initial=date.today)
    fecha_to = forms.DateField(widget=forms.DateInput(format='%d-%m-%Y'), input_formats=('%d-%m-%Y',),
                               initial=date.today)
    fecha = forms.DateField(widget=forms.DateInput(format='%d-%m-%Y'),
                            input_formats=('%d-%m-%Y',),
                            initial=date.today,
                            label='Fecha del informe')
    fotos = forms.BooleanField(label='¿Incluir fotos?',required=False)
    reparadas = forms.BooleanField(label='¿Incluir observaciones solucionadas?',required=False)
    colores = forms.BooleanField(label='¿Incluir código de colores?', required=False)
    estados = forms.BooleanField(label='¿Incluir columna con el estado?', required=False)

    def __init__(self, *args, **kwargs):
        parque = kwargs.pop('parque')
        super(Punchlist, self).__init__(*args, **kwargs)
        try:
            obj = ConfiguracionFU.objects.get(parque=parque)
            self.fields['fecha_from'].initial = obj.fecha_inicio
        except ConfiguracionFU.DoesNotExist:
            logger.debug("ConfiguracionFU para parque no existe, queda todo igual")

        self.fields['aerogenerador'].queryset = Aerogenerador.objects.filter(parque=parque).order_by('idx')
        self.fields['fotos'].widget.attrs['class'] = 'make-switch'
        self.fields['fotos'].widget.attrs['data-size'] = 'small'
        self.fields['fotos'].widget.attrs['data-on-text'] = 'Si'
        self.fields['fotos'].widget.attrs['data-off-text'] = 'No'
        self.fields['fotos'].widget.attrs['checked'] = ''
        self.fields['reparadas'].widget.attrs['class'] = 'make-switch'
        self.fields['reparadas'].widget.attrs['data-size'] = 'small'
        self.fields['reparadas'].widget.attrs['data-on-text'] = 'Si'
        self.fields['reparadas'].widget.attrs['data-off-text'] = 'No'
        self.fields['colores'].widget.attrs['class'] = 'make-switch'
        self.fields['colores'].widget.attrs['data-size'] = 'small'
        self.fields['colores'].widget.attrs['data-on-text'] = 'Si'
        self.fields['colores'].widget.attrs['data-off-text'] = 'No'
        self.fields['colores'].widget.attrs['checked'] = ''
        self.fields['fecha'].widget.attrs['class'] = 'form-control'
        self.fields['fecha'].widget.attrs['readonly'] = True
        self.fields['fecha_from'].widget.attrs['class'] = 'form-control'
        self.fields['fecha_from'].widget.attrs['readonly'] = True
        self.fields['fecha_to'].widget.attrs['class'] = 'form-control'
        self.fields['fecha_to'].widget.attrs['readonly'] = True
        self.fields['estados'].widget.attrs['class'] = 'make-switch'
        self.fields['estados'].widget.attrs['data-size'] = 'small'
        self.fields['estados'].widget.attrs['data-on-text'] = 'Si'
        self.fields['estados'].widget.attrs['data-off-text'] = 'No'
        self.fields['estados'].widget.attrs['checked'] = ''