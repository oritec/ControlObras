# -*- coding: utf-8 -*-
from django.forms import ModelForm, Textarea, TextInput, HiddenInput, DateInput, Select, NumberInput, Form
from django.forms.widgets import PasswordInput, TextInput,CheckboxInput
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.utils.translation import gettext as _
from django.contrib.auth import login, authenticate, logout

import datetime
import logging

logger = logging.getLogger('oritec')

class LoginForm(Form):
    username = forms.CharField(widget=TextInput(attrs={'class': 'form-control placeholder-no-fix"'}))
    password = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control placeholder-no-fix"'}),required=True)
    
    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is None or not user.is_active:
            raise forms.ValidationError("Usuario o contraseña incorrectos. Por favor, intenta de nuevo.")
        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user
