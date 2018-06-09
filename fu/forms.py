# -*- coding: utf-8 -*-
from django import forms
from vista.models import ParqueSolar,Aerogenerador
from fu.models import ComponentesParque, Componente,RelacionesFU,ConfiguracionFU
from fu.models import EstadoFU, Registros, Paradas
from datetime import date
import logging
logger = logging.getLogger('oritec')

class ComponenteForm(forms.Form):
    estadofu = forms.ModelMultipleChoiceField(queryset=EstadoFU.objects.filter(idx__gte=1,idx__lte=4).order_by('idx'),
                                              widget=forms.CheckboxSelectMultiple,required=False)
    nombre = forms.CharField(max_length=100)
    def __init__(self, *args, **kwargs):
        super(ComponenteForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs['class'] = 'form-control'

class AddComponentesForm(forms.Form):
    componente = forms.ModelChoiceField(queryset=None)
    def __init__(self, *args, **kwargs):
        parque = kwargs.pop('parque')
        aux = ComponentesParque.objects.get(parque=parque)
        list_id = []
        for r in aux.componentes.all():
            list_id.append(r.id)
        super(AddComponentesForm, self).__init__(*args, **kwargs)
        self.fields['componente'].queryset = Componente.objects.exclude(id__in=list_id)
        self.fields['componente'].widget.attrs['class'] = 'bs-select form-control'

class DeleteComponentesForm(forms.Form):
    componente = forms.ModelChoiceField(queryset=None)
    def __init__(self, *args, **kwargs):
        parque = kwargs.pop('parque')
        aux = ComponentesParque.objects.get(parque=parque)
        list_id = []
        for r in aux.componentes.all():
            list_id.append(r.id)
        super(DeleteComponentesForm, self).__init__(*args, **kwargs)
        self.fields['componente'].queryset = Componente.objects.filter(id__in=list_id)
        self.fields['componente'].widget.attrs['class'] = 'bs-select form-control'

class ConfiguracionFUForm(forms.ModelForm):
    fecha_inicio = forms.DateField(widget=forms.DateInput(format='%d-%m-%Y'),
                                  input_formats=('%d-%m-%Y',))
    fecha_final = forms.DateField(widget=forms.DateInput(format = '%d-%m-%Y'),
                                 input_formats=('%d-%m-%Y',))
    class Meta:
        model = ConfiguracionFU
        fields = ['fecha_inicio','fecha_final']
        labels = {
            'fecha_inicio': 'Fecha Inicio del Proyecto',
            'fecha_final': 'Fecha Final del Proyecto',
        }
    def __init__(self, *args, **kwargs):
        super(ConfiguracionFUForm, self).__init__(*args, **kwargs)
        self.fields['fecha_inicio'].widget.attrs['class'] = 'form-control'
        self.fields['fecha_inicio'].widget.attrs['readonly'] = True
        self.fields['fecha_final'].widget.attrs['class'] = 'form-control'
        self.fields['fecha_final'].widget.attrs['readonly'] = True

class PlanificacionForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionFU
        fields = ['plan']
        labels = {
            'plan': 'Archivo Planificación',
        }
    def __init__(self, *args, **kwargs):
        super(PlanificacionForm, self).__init__(*args, **kwargs)

class RegistroForm(forms.ModelForm):
    fecha = forms.DateField(widget=forms.DateInput(format='%d-%m-%Y'),
                                  input_formats=('%d-%m-%Y',))
    class Meta:
        model = Registros
        fields = ['fecha']
    def __init__(self, *args, **kwargs):
        super(RegistroForm, self).__init__(*args, **kwargs)
        self.fields['fecha'].widget.attrs['class'] = 'form-control'
        self.fields['fecha'].widget.attrs['readonly'] = True

class RegistroDescargaForm(forms.ModelForm):
    fecha = forms.DateField(widget=forms.DateInput(format='%d-%m-%Y'),
                                  input_formats=('%d-%m-%Y',))
    class Meta:
        model = Registros
        fields = ['fecha','no_serie']
    def __init__(self, *args, **kwargs):
        super(RegistroDescargaForm, self).__init__(*args, **kwargs)
        self.fields['fecha'].widget.attrs['class'] = 'form-control'
        self.fields['fecha'].widget.attrs['readonly'] = True
        self.fields['no_serie'].widget.attrs['class'] = 'form-control'

class ParadasForm(forms.ModelForm):
    fecha_inicio = forms.DateTimeField(widget=forms.DateTimeInput(format='%d-%m-%Y %H:%M'),
                                        input_formats=('%d-%m-%Y %H:%M',))
    fecha_final = forms.DateTimeField(widget=forms.DateTimeInput(format='%d-%m-%Y %H:%M'),
                                       input_formats=('%d-%m-%Y %H:%M',))
    class Meta:
        model = Paradas
        fields = ['parque','fecha_inicio','fecha_final','aerogenerador','componente','trabajo','motivo','grua','observaciones']

    def __init__(self, *args, **kwargs):
        super(ParadasForm, self).__init__(*args, **kwargs)

        if 'initial' in kwargs:
            parque = kwargs['initial']['parque']
            self.fields['aerogenerador'].queryset = Aerogenerador.objects.filter(parque=parque)
        elif 'instance' in kwargs:
            parque = kwargs['instance'].parque
            self.fields['aerogenerador'].queryset = Aerogenerador.objects.filter(parque=parque)

        self.fields['parque'].widget = forms.HiddenInput()
        self.fields['fecha_inicio'].widget.attrs['class'] = 'form-control'
        self.fields['fecha_inicio'].widget.attrs['readonly'] = True
        self.fields['fecha_final'].widget.attrs['class'] = 'form-control'
        self.fields['fecha_final'].widget.attrs['readonly'] = True
        self.fields['aerogenerador'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['aerogenerador'].widget.attrs['data-live-search'] = 'true'
        self.fields['aerogenerador'].widget.attrs['data-size'] = '8'
        self.fields['componente'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['componente'].widget.attrs['data-live-search'] = 'true'
        self.fields['componente'].widget.attrs['data-size'] = '8'
        self.fields['trabajo'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['trabajo'].widget.attrs['data-live-search'] = 'true'
        self.fields['trabajo'].widget.attrs['data-size'] = '8'
        self.fields['grua'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['grua'].widget.attrs['data-live-search'] = 'true'
        self.fields['grua'].widget.attrs['data-size'] = '8'
        self.fields['motivo'].widget.attrs['class'] = 'form-control'
        self.fields['observaciones'].widget = forms.Textarea()
        self.fields['observaciones'].widget.attrs['class'] = 'form-control'
        self.fields['observaciones'].widget.attrs['row'] = '3'

class ReporteForm(forms.Form):

    fecha = forms.DateField(widget=forms.DateInput(format='%d-%m-%Y'),
                            input_formats=('%d-%m-%Y',),
                            initial=date.today,
                            label='Fecha')
    nombre_archivo = forms.CharField(max_length=50,required=False)
    def __init__(self, *args, **kwargs):
        super(ReporteForm, self).__init__(*args, **kwargs)

        self.fields['fecha'].widget.attrs['class'] = 'form-control'
        self.fields['fecha'].widget.attrs['readonly'] = True
        self.fields['nombre_archivo'].widget.attrs['class'] = 'form-control'
