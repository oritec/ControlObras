# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from vista.models import Aerogenerador

import logging
logger = logging.getLogger('oritec')

@python_2_unicode_compatible
class DR(models.Model):
    parque = models.ForeignKey('vista.ParqueSolar', on_delete=models.CASCADE)
    fecha = models.DateField(blank=False, null=False)
    numero = models.IntegerField()
    climatologia = models.CharField(max_length=100, unique=False)
    sitio = models.CharField(max_length=100, unique=False)
    actividades = models.CharField(max_length=500, unique=False)
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return '%s' % (self.actividades)


@python_2_unicode_compatible
class ActividadDR(models.Model):
    descripcion = models.CharField(max_length=500, unique=False)
    dr = models.ForeignKey('DR', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return '%s' % (self.descripcion)

@python_2_unicode_compatible
class ComposicionDR(models.Model):
    actividad = models.ForeignKey('ActividadDR', on_delete=models.CASCADE)
    pie = models.CharField(max_length=200, unique=False)
    tipo = models.CharField(max_length=10, unique=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return '%s' % (self.descripcion)

def dr_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'dr/dr_{0}/actividad_{1}/{2}'.format(instance.composicion.actividad.dr.id,
                                      instance.composicion.actividad.id,
                                      filename)

def thumbnail_dr_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'dr/dr_{0}/actividad_{1}/thumbnails/{2}'.format(instance.composicion.actividad.dr.id,
                                                instance.composicion.actividad.id,
                                                filename)

@python_2_unicode_compatible
class FotosDR(models.Model):
    composicion = models.ForeignKey('ComposicionDR', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to=dr_path)
    thumbnail = models.ImageField(upload_to=thumbnail_dr_path, max_length=500, null=True, blank=True)
    orden = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return '%s' % (self.descripcion)