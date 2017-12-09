# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.template import defaultfilters
import logging
logger = logging.getLogger('oritec')


@python_2_unicode_compatible
class Aerogenerador(models.Model):
    idx = models.IntegerField()
    nombre = models.CharField(max_length=100)
    parque = models.ForeignKey('ParqueSolar', on_delete=models.CASCADE)
    slug = models.SlugField()
    class Meta:
        unique_together = (("parque", "idx"),("parque", "nombre"))
    def __str__(self):
        return '%s' % (self.nombre)
    def graphText(self):
        return '%s' % (self.nombre)
    def save(self, *args, **kwargs):
        self.slug = defaultfilters.slugify(self.nombre)
        super(Aerogenerador, self).save(*args, **kwargs)

def logos_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'logos/{0}'.format(filename)

def word_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'word/{0}'.format(filename)

def excel_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'excel/{0}'.format(filename)

@python_2_unicode_compatible
class ParqueSolar(models.Model):
    nombre = models.CharField(max_length=50)
    slug = models.SlugField(unique=True,null=True)
    cliente = models.CharField(max_length=100, default='')
    suministrador = models.CharField(max_length=100, default='')
    plataforma = models.CharField(max_length=100, default='')
    no_aerogeneradores = models.IntegerField(default=0)
    prev_no_aerogeneradores = models.IntegerField(default=0)
    codigo = models.CharField(max_length=50,unique=True)
    logo = models.ImageField(upload_to=logos_directory_path, max_length=500, null=True, blank=True)
    word = models.FileField(upload_to=word_directory_path, max_length=500, null=True, blank=True)
    excel_fu = models.FileField(upload_to=excel_directory_path, max_length=500, null=True, blank=True)
    pais = models.CharField(max_length=100, default='')
    region = models.CharField(max_length=100, default='')
    municipio = models.CharField(max_length=100, default='')
    class Meta:
        unique_together = (("nombre", "codigo"))
    def __str__(self):
        return '%s' % (self.nombre)

    def getPrintName(self):
        return self.codigo + " " + self.nombre

    def save(self, *args, **kwargs):
        self.slug = defaultfilters.slugify(self.codigo)
        super(ParqueSolar, self).save(*args, **kwargs)
