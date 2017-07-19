# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.template import defaultfilters
import logging
logger = logging.getLogger('oritec')


@python_2_unicode_compatible
class ParqueSolar(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField()
    cliente = models.CharField(max_length=100, default='')
    suministrador = models.CharField(max_length=100, default='')
    plataforma = models.CharField(max_length=100, default='')
    no_aerogeneradores = models.IntegerField(default=0)

    def __str__(self):
        return '%s' % (self.nombre)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = defaultfilters.slugify(self.nombre)
        super(ParqueSolar, self).save(*args, **kwargs)
