# -*- coding: utf-8 -*-

from django.conf.urls import url
from dr import views

urlpatterns = [
    url(r'^editar/actividad/ajax', views.actividad_ajax, name='actividad_ajax'),
    url(r'^editar/composicion/ajax', views.composicion_ajax, name='composicion_ajax'),
    url(r'^editar/(?P<dr_id>[0-9]+)/actividad/composicion/agregar', views.composicion_agregar, name='composicion_agregar'),
    url(r'^editar/(?P<dr_id>[0-9]+)/ordenar', views.dr_ordenar, name='dr_ordenar'),
    url(r'^editar/(?P<dr_id>[0-9]+)/actividad/agregar', views.actividad_agregar, name='actividad_agregar'),
    url(r'^editar/(?P<dr_id>[0-9]+)/actividad/eliminar', views.actividad_eliminar, name='actividad_eliminar'),
    url(r'^editar/(?P<dr_id>[0-9]+)/composicion/eliminar', views.composicion_eliminar, name='composicion_eliminar'),
    url(r'^editar/(?P<dr_id>[0-9]+)', views.editar, name='editar'),
    url(r'^reporte/(?P<dr_id>[0-9]+)', views.create_dr_word, name='reporte_dr_word'),
    url(r'^listado', views.listado, name='listado'),
    url(r'^agregar', views.agregar, name='agregar'),
    url(r'^borrar', views.borrar, name='borrar'),
]