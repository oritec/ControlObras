# -*- coding: utf-8 -*-

from django.conf.urls import url
from dr import views

urlpatterns = [
    url(r'^editar/(?P<dr_id>[0-9]+)', views.editar, name='dr-editar'),
    url(r'^listado', views.listado, name='listado'),
    url(r'^agregar', views.agregar, name='agregar'),

]