# -*- coding: utf-8 -*-

from django.conf.urls import url
from ncr import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^observaciones/resumen', views.observaciones_resumen, name='observaciones-resumen'),
    url(r'^observaciones/imagenes/ver', views.list_fotos, name='fotos-list'),
    url(r'^observaciones/(?P<observacion_id>[0-9]+)/ver', views.show_observacion, name='observaciones-show'),
    url(r'^observaciones/(?P<observacion_id>[0-9]+)/revision/agregar', views.add_revision, name='revisiones-add'),
    url(r'^observaciones/(?P<ag_id>[0-9]+)', views.observaciones, name='observaciones'),
    url(r'^observaciones/agregar', views.add_observacion, name='observaciones-agregar'),
    url(r'^observaciones/imagenes/set_primary', views.primary_image, name='imagenes-primary'),
    url(r'^observaciones/imagenes/(?P<image_id>[0-9]+)/borrar', views.del_image, name='imagenes-delete'),
    url(r'^revision/(?P<revision_id>[0-9]+)/imagenes/agregar', views.add_images, name='imagenes-agregar'),
]