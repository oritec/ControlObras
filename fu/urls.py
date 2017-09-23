# -*- coding: utf-8 -*-

from django.conf.urls import url
from fu import views

urlpatterns = [
    url(r'^componentes', views.componente, name='componentes'),
    url(r'^actividades/(?P<estado>[-\w\d]+)/ordenar', views.ordenar_actividades, name='actividades-ordenar'),
    url(r'^actividades', views.actividades, name='actividades'),

    #url(r'^componente/crear', views.create_componente, name='componente-create')
]