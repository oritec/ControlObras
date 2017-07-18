# -*- coding: utf-8 -*-

from django.conf.urls import url
from vista import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^parque/borrar', views.del_parque, name='del_parque'),
    url(r'^parque/(?P<slug>[-\w\d]+)/', views.home, name='home'),
]
