# -*- coding: utf-8 -*-
from django import forms
from models import ParqueSolar

class ParqueFormFull(forms.ModelForm):
    class Meta:
        model = ParqueSolar
        fields = ['nombre','cliente','suministrador','plataforma','no_aerogeneradores','codigo','logo','word','pais','region','municipio']
        labels = {
            'no_aerogeneradores': 'Nº de Aerogeneradores',
            'word': 'Plantilla Word Informes'
        }
    def __init__(self, *args, **kwargs):
        super(ParqueFormFull, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs['class'] = 'form-control'
        self.fields['cliente'].widget.attrs['class'] = 'form-control'
        self.fields['suministrador'].widget.attrs['class'] = 'form-control'
        self.fields['plataforma'].widget.attrs['class'] = 'form-control'
        self.fields['no_aerogeneradores'].widget.attrs['class'] = 'form-control'
        self.fields['codigo'].widget.attrs['class'] = 'form-control'
        self.fields['pais'].widget.attrs['class'] = 'form-control'
        self.fields['region'].widget.attrs['class'] = 'form-control'
        self.fields['municipio'].widget.attrs['class'] = 'form-control'


class ParqueForm(forms.ModelForm):
    class Meta:
        model = ParqueSolar
        fields = ['nombre']
    def __init__(self, *args, **kwargs):
        super(ParqueForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs['class'] = 'form-control'
