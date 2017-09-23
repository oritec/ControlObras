# -*- coding: utf-8 -*-
from django import forms
from vista.models import ParqueSolar,Aerogenerador
from fu.models import ComponentesParque, Componente,RelacionesFU
from fu.models import EstadoFU
import logging
logger = logging.getLogger('oritec')

class ComponenteForm(forms.Form):
    estadofu = forms.ModelMultipleChoiceField(queryset=EstadoFU.objects.filter(idx__gte=1,idx__lte=4).order_by('idx'),
                                              widget=forms.CheckboxSelectMultiple,required=False)
    nombre = forms.CharField(max_length=100)
    def __init__(self, *args, **kwargs):
        super(ComponenteForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs['class'] = 'form-control'

class ActividadesComponentesForm(forms.Form):
    componente = forms.ModelChoiceField(queryset=None)
    def __init__(self, *args, **kwargs):
        parque = kwargs.pop('parque')
        aux = ComponentesParque.objects.get(parque=parque)
        list_id = []
        for r in aux.componentes.all():
            list_id.append(r.id)
        super(ActividadesComponentesForm, self).__init__(*args, **kwargs)
        self.fields['componente'].queryset = Componente.objects.exclude(id__in=list_id)
        self.fields['componente'].widget.attrs['class'] = 'bs-select form-control'