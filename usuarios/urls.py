# -*- coding: utf-8 -*-

from django.conf.urls import url
from usuarios import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^usuarios/agregar', views.usuario_agregar, name='usuario-agregar'),
    url(r'^usuarios/(?P<usuario_id>[0-9]+)/editar', views.usuario_editar, name='usuario-editar'),
    url(r'^usuarios/borrar', views.usuario_borrar, name='usuario-borrar'),
    url(r'^usuarios/cambiar_contrasena', views.usuario_cambiarcontrasena, name='usuario-cambiarcontrasena'),
    url(r'^usuarios', views.usuarios, name='usuarios'),
]