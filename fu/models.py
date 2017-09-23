# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from vista.models import ParqueSolar

import logging
logger = logging.getLogger('oritec')

@python_2_unicode_compatible
class EstadoFU(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    idx = models.IntegerField(unique=True)
    def __str__(self):
        return '%s' % (self.nombre)

@python_2_unicode_compatible
class Componente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    estados = models.ManyToManyField(EstadoFU)
    def __str__(self):
        return '%s' % (self.nombre)

@python_2_unicode_compatible
class ComponentesParque(models.Model):
    parque = models.OneToOneField(ParqueSolar, on_delete=models.CASCADE)
    componentes = models.ManyToManyField(Componente,through='RelacionesFU',through_fields=('componentes_parque','componente'))
    def __str__(self):
        return 'Componentes Parque ' + '%s' % (self.parque.nombre)

@python_2_unicode_compatible
class RelacionesFU(models.Model):
    componentes_parque = models.ForeignKey(ComponentesParque, on_delete=models.CASCADE)
    componente = models.ForeignKey(Componente, on_delete=models.CASCADE)
    orden_descarga = models.SmallIntegerField()
    orden_premontaje = models.SmallIntegerField()
    orden_montaje = models.SmallIntegerField()
    orden_puestaenmarcha = models.SmallIntegerField()
    class Meta:
        unique_together = ("componentes_parque", "componente")
    def __str__(self):
        return 'Relaciones Componentes Parque ' + '%s' % (self.componentes_parque.parque.nombre)