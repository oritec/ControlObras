# -*- coding: utf-8 -*-

from django.conf.urls import url
from fu import views

urlpatterns = [
    url(r'^avance', views.avance, name='avance'),
    url(r'^dashboard_diario', views.dashboard_diario, name='dashboard-diario'),
    url(r'^dashboard_imagen', views.dashboard_imagen, name='dashboard-imagen'),
    url(r'^dashboard', views.dashboard, name='dashboard'),
    url(r'^componentes', views.componente, name='componentes'),
    url(r'^actividades/registro/(?P<slug_ag>[-\w\d]+)', views.ingreso, name='ingreso'),
    url(r'^actividades/(?P<str_estado>[-\w\d]+)/ordenar', views.ordenar_actividades, name='actividades-ordenar'),
    url(r'^actividades', views.actividades, name='actividades'),
    url(r'^planificacion', views.planificacion, name='planificacion'),
    url(r'^configuracion', views.configuracion, name='configuracion'),
    url(r'^download_config', views.download_config, name='download_config'),
    url(r'^planificacion', views.planificacion, name='planificacion'),
    url(r'^paradas/agregar', views.add_paradas, name='agregar-paradas'),
    url(r'^paradas/(?P<id>[0-9]+)/editar', views.edit_paradas, name='editar-paradas'),
    url(r'^paradas', views.paradas, name='paradas'),
    url(r'^reportes', views.reportes, name='reportes'),
    url(r'^status_componentes', views.status_componentes, name='status_componentes'),
    # url(r'^componente/crear', views.create_componente, name='componente-create')
]