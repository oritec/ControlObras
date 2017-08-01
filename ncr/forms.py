# -*- coding: utf-8 -*-
from django import forms
from models import Observacion, Revision,EstadoRevision
import logging
logger = logging.getLogger('oritec')

class ObservacionForm(forms.ModelForm):
    fecha_observacion = forms.DateField(widget=forms.DateInput(format = '%d-%m-%Y'),
                                 input_formats=('%d-%m-%Y',))
    class Meta:
        model = Observacion
        fields = ['parque','nombre','aerogenerador','fecha_observacion','componente','sub_componente','tipo','punchlist']
        labels = {
            'nombre': 'Descripción',
        }
    def __init__(self, *args, **kwargs):
        super(ObservacionForm, self).__init__(*args, **kwargs)

        parque = kwargs['initial']['parque']

        opciones = []
        for ag in range(1,parque.no_aerogeneradores+1):
            #logger.debug(ag)
            opciones.append((ag,'WTG'+str(ag).zfill(2)))
        self.fields['aerogenerador'] = forms.ChoiceField(
            choices=opciones
        )
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
        self.fields['tipo'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['tipo'].widget.attrs['data-live-search'] = 'true'
        self.fields['tipo'].widget.attrs['data-size'] = '8'
        self.fields['punchlist'].widget.attrs['class'] = 'make-switch'
        self.fields['punchlist'].widget.attrs['data-size'] = 'small'
        self.fields['punchlist'].widget.attrs['data-on-text'] = 'Si'
        self.fields['punchlist'].widget.attrs['data-off-text'] = 'No'

class RevisionForm(forms.ModelForm):
    fecha_revision = forms.DateField(widget=forms.HiddenInput(),
                                        input_formats=('%d-%m-%Y',))
    class Meta:
        model = Revision
        fields = ['fecha_revision','severidad','descripcion']
        labels = {
            'descripcion': 'Detalle',
        }
    def __init__(self, *args, **kwargs):
        super(RevisionForm, self).__init__(*args, **kwargs)
        #self.fields['fecha_revision'].widget = forms.HiddenInput()
        self.fields['severidad'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['severidad'].widget.attrs['data-live-search'] = 'true'
        self.fields['severidad'].widget.attrs['data-size'] = '8'
        self.fields['descripcion'].widget = forms.Textarea()
        self.fields['descripcion'].widget.attrs['class'] = 'form-control'
        self.fields['descripcion'].widget.attrs['row'] = '3'

class RevisionFormFull(forms.ModelForm):
    fecha_revision = forms.DateField(widget=forms.DateInput(format = '%d-%m-%Y'),
                                 input_formats=('%d-%m-%Y',))
    class Meta:
        model = Revision
        fields = ['observacion','fecha_revision','severidad','descripcion', 'estado']
        labels = {
            'descripcion': 'Detalle',
        }
    def __init__(self, *args, **kwargs):
        super(RevisionFormFull, self).__init__(*args, **kwargs)
        self.fields['observacion'].widget = forms.HiddenInput()
        self.fields['severidad'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['severidad'].widget.attrs['data-live-search'] = 'true'
        self.fields['severidad'].widget.attrs['data-size'] = '8'
        self.fields['descripcion'].widget = forms.Textarea()
        self.fields['descripcion'].widget.attrs['class'] = 'form-control'
        self.fields['descripcion'].widget.attrs['row'] = '3'
        self.fields['fecha_revision'].widget.attrs['class'] = 'form-control'
        self.fields['estado'].widget.attrs['class'] = 'bs-select form-control'

class NCR(forms.Form):
    aerogenerador = forms.ChoiceField(choices=[])
    parque = forms.ModelChoiceField(queryset=EstadoRevision.objects.all(), empty_label=None)
    def __init__(self, *args, **kwargs):
        super(NCR, self).__init__(*args, **kwargs)

        self.fields['parque'].widget.attrs['class'] = 'selectpicker form-control'