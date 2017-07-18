# -*- coding: utf-8 -*-
from django import forms
from models import ParqueSolar
from django.template import defaultfilters

class ParqueChoiceForm(forms.Form):
    parque = forms.ModelChoiceField(queryset=ParqueSolar.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        super(ParqueChoiceForm, self).__init__(*args, **kwargs)
        self.fields['parque'].widget.attrs['class'] = 'selectpicker form-control'

class ParqueForm(forms.ModelForm):
    class Meta:
        model = ParqueSolar
        fields = ['nombre']
    def __init__(self, *args, **kwargs):
        super(ParqueForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs['class'] = 'form-control'