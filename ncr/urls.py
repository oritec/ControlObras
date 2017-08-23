# -*- coding: utf-8 -*-

from django.conf.urls import url
from ncr import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^observaciones/resumen', views.observaciones_resumen, name='observaciones-resumen'),
    url(r'^observaciones/imagenes/ver', views.list_fotos, name='fotos-list'),
    url(r'^observaciones/(?P<observacion_id>[0-9]+)/ver', views.show_observacion, name='observaciones-show'),
    url(r'^observaciones/(?P<observacion_id>[0-9]+)/editar', views.add_observacion, name='observaciones-editar'),
    url(r'^observaciones/(?P<observacion_id>[0-9]+)/revision/agregar', views.add_revision, name='revisiones-add'),
    url(r'^observaciones/(?P<observacion_id>[0-9]+)/revision/(?P<revision_id>[0-9]+)/editar', views.add_revision, name='revisiones-editar'),
    url(r'^observaciones/agregar', views.add_observacion, name='observaciones-agregar'),
    url(r'^observaciones/eliminar', views.del_observacion, name='observaciones-eliminar'),
    url(r'^observaciones/cerrar', views.close_observacion, name='observaciones-cerrar'),
    url(r'^observaciones/imagenes/set_primary', views.primary_image, name='imagenes-primary'),
    url(r'^observaciones/imagenes/(?P<image_id>[0-9]+)/borrar', views.del_image, name='imagenes-delete'),
    url(r'^revision/(?P<revision_id>[0-9]+)/imagenes/agregar', views.add_images, name='imagenes-agregar'),
    url(r'^revision/eliminar', views.del_revision, name='revision-eliminar'),
    url(r'^observaciones/informeNCR', views.informeNCR, name='informeNCR'),
    url(r'^observaciones/punchlist', views.punchlist, name='punchlist'),
    url(r'^observaciones/(?P<slug_ag>[-\w\d]+)', views.observaciones, name='observaciones'),
    url(r'^observadores', views.observadores, name='observadores')
]