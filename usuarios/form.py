# -*- coding: utf-8 -*-
from django.forms import ModelForm, Textarea, TextInput, HiddenInput, DateInput, Select, NumberInput, Form
from django.forms.widgets import PasswordInput, TextInput,CheckboxInput
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.utils.translation import gettext as _
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import Group
from vista.models import ParqueSolar
from django.contrib.auth.models import User

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

class EditUsuarioForm(Form):
    nombre = forms.CharField()
    perfil = forms.ChoiceField()
    proyectos = forms.MultipleChoiceField(required=False, label='Proyectos autorizados')

    def __init__(self, *args, **kwargs):

        if 'usuario' in kwargs:
            usuario = kwargs.pop('usuario', None)
            opciones1 = []
            opciones2 = []
            group = Group.objects.get(name='Usuario 1')

            if usuario.user.is_superuser:
                groups = Group.objects.all()
                opciones1.append((0,'Administrador'),)
                for g in groups:
                    opciones1.append((g.id,g.name),)
                for p in ParqueSolar.objects.all():
                    opciones2.append((p.id, p.nombre), )
            elif group in usuario.user.groups.all():
                groups = Group.objects.all().exclude(name__exact='Usuario 1')
                for g in groups:
                    opciones1.append((g.id,g.name),)
                for p in ParqueSolar.objects.all():
                    opciones2.append((p.id, p.nombre), )

        if 'edit' in kwargs:
            usuario_edit = kwargs.pop('edit', None)
            if usuario_edit.user.is_superuser:
                perfil = 'Administrador'
            else:
                g = usuario_edit.user.groups.all()[0]
                perfil=g.id
            proyectos=[]
            for parque in usuario_edit.parques.all():
                proyectos.append(parque.id)
            kwargs.update(initial={
                # 'field': 'value'
                'nombre': usuario_edit.user.username,
                'perfil': perfil,
                'proyectos':proyectos,
            })

        super(EditUsuarioForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs['class'] = 'form-control'
        self.fields['perfil'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['perfil'].choices= opciones1
        self.fields['proyectos'].choices = opciones2

class NewUsuarioForm(Form):
    nombre = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput(attrs={'required': 'true'}), required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'required': 'true'}),required=True )

    perfil = forms.ChoiceField()
    proyectos = forms.MultipleChoiceField(required=False, label='Proyectos autorizados')

    def __init__(self, *args, **kwargs):
        if 'usuario' in kwargs:
            usuario = kwargs.pop('usuario', None)
            opciones1 = []
            opciones2 = []
            group = Group.objects.get(name='Usuario 1')

            if usuario.user.is_superuser:
                groups = Group.objects.all()
                opciones1.append((0,'Administrador'),)
                for g in groups:
                    opciones1.append((g.id,g.name),)
                for p in ParqueSolar.objects.all():
                    opciones2.append((p.id, p.nombre), )
            elif group in usuario.user.groups.all():
                groups = Group.objects.all().exclude(name__exact='Usuario 1')
                for g in groups:
                    opciones1.append((g.id,g.name),)
                for p in usuario.parques.all():
                    opciones2.append((p.id, p.nombre), )

        if 'edit' in kwargs:
            usuario_edit = kwargs.pop('edit', None)
            if usuario_edit.user.is_superuser:
                perfil = 'Administrador'
            else:
                g = usuario_edit.user.groups.all()[0]
                perfil=g.id
            proyectos=[]
            for parque in usuario_edit.parques.all():
                proyectos.append(parque.id)
            kwargs.update(initial={
                # 'field': 'value'
                'nombre': usuario_edit.user.username,
                'perfil': perfil,
                'proyectos':proyectos,
            })

        super(NewUsuarioForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'
        self.fields['password_confirm'].widget.attrs['class'] = 'form-control'
        self.fields['perfil'].widget.attrs['class'] = 'bs-select form-control'
        self.fields['perfil'].choices= opciones1
        self.fields['proyectos'].choices = opciones2

    def clean_nombre(self):
        data = self.cleaned_data['nombre']
        if User.objects.filter(username__exact=data).count()>0:
            raise forms.ValidationError("Nombre ya existe!")

        return data

    def clean(self):
        cleaned_data = super(NewUsuarioForm, self).clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("Las dos contraseñas deben ser iguales.")
        return cleaned_data

class ChangePasswordForm(Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'required': 'true'}), required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'required': 'true'}),required=True )

    def __init__(self, *args, **kwargs):

        super(ChangePasswordForm, self).__init__(*args, **kwargs)

        self.fields['password'].widget.attrs['class'] = 'form-control'
        self.fields['password_confirm'].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("Las dos contraseñas deben ser iguales.")
        return cleaned_data