# -*- coding: utf-8 -*-

from django.conf.urls import url
from fu import views

urlpatterns = [
    url(r'^componentes', views.componente, name='componentes'),
    url(r'^actividades/(?P<estado>[-\w\d]+)/ordenar', views.ordenar_actividades, name='actividades-ordenar'),
    url(r'^actividades', views.actividades, name='actividades'),
    url(r'^planificacion', views.planificacion, name='planificacion'),
    url(r'^configuracion', views.configuracion, name='configuracion'),
    url(r'^download_config', views.download_config, name='download_config'),
    #url(r'^componente/crear', views.create_componente, name='componente-create')
]