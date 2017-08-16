# -*- coding: utf-8 -*-
from django import forms
from models import ParqueSolar

class ParqueFormFull(forms.ModelForm):
    class Meta:
        model = ParqueSolar
        fields = ['nombre','cliente','suministrador','plataforma','no_aerogeneradores','codigo']
        labels = {
            'no_aerogeneradores': 'Nº de Aerogeneradores',
        }
    def __init__(self, *args, **kwargs):
        super(ParqueFormFull, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs['class'] = 'form-control'
        self.fields['cliente'].widget.attrs['class'] = 'form-control'
        self.fields['suministrador'].widget.attrs['class'] = 'form-control'
        self.fields['plataforma'].widget.attrs['class'] = 'form-control'
        self.fields['no_aerogeneradores'].widget.attrs['class'] = 'form-control'
        self.fields['codigo'].widget.attrs['class'] = 'form-control'

class ParqueForm(forms.ModelForm):
    class Meta:
        model = ParqueSolar
        fields = ['nombre']
    def __init__(self, *args, **kwargs):
        super(ParqueForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs['class'] = 'form-control'
