# -*- coding: utf-8 -*-
from django import forms
from dr.models import DR
import logging
from datetime import date
logger = logging.getLogger('oritec')

class DRForm(forms.ModelForm):
    fecha = forms.DateField(widget=forms.DateInput(format='%d-%m-%Y'),
                                        input_formats=('%d-%m-%Y',))

    class Meta:
        model = DR
        fields = ['parque','fecha', 'numero', 'climatologia','sitio','actividades', 'hora_entrada', 'hora_salida']
        labels = {
            'actividades': 'Actividades Principales',
            'numero': 'Número',
        }

    def __init__(self, *args, **kwargs):
        super(DRForm, self).__init__(*args, **kwargs)
        self.fields['parque'].widget = forms.HiddenInput()
        self.fields['fecha'].widget.attrs['class'] = 'form-control'
        self.fields['fecha'].widget.attrs['readonly'] = True
        self.fields['numero'].widget.attrs['class'] = 'form-control'
        self.fields['climatologia'].widget.attrs['class'] = 'form-control'
        self.fields['sitio'].widget.attrs['class'] = 'form-control'
        self.fields['actividades'].widget.attrs['class'] = 'form-control'
        self.fields['hora_entrada'].widget.attrs['class'] = 'form-control timepicker'
        self.fields['hora_salida'].widget.attrs['class'] = 'form-control timepicker'


