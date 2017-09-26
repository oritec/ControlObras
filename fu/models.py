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

def plan_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'planificacion/{0}'.format(filename)

@python_2_unicode_compatible
class ConfiguracionFU(models.Model):
    parque = models.ForeignKey('vista.ParqueSolar', on_delete=models.CASCADE)
    fecha_inicio = models.DateField(blank=False, null=False)
    fecha_final = models.DateField(blank=False, null=False)
    plan = models.FileField(upload_to=plan_directory_path, max_length=500, null=True, blank=True)
    prev_plan = models.FileField(upload_to=plan_directory_path, max_length=500, null=True, blank=True)
    def __str__(self):
        return 'Configuracion'
    def save(self, *args, **kwargs):
        if self.plan:
            self.prev_plan = self.__class__._default_manager.filter(pk=self.pk).values('plan').get()['plan']
        super(ConfiguracionFU, self).save(*args, **kwargs)  # Call the "real" save() method.

@python_2_unicode_compatible
class Plan(models.Model):
    parque = models.ForeignKey(ParqueSolar, on_delete=models.CASCADE)
    componente = models.ForeignKey(Componente, on_delete=models.CASCADE)
    estado = models.ForeignKey(EstadoFU, on_delete=models.CASCADE)
    fecha = models.DateField(blank=False, null=False)
    no_aerogeneradores = models.SmallIntegerField()
    class Meta:
        unique_together = ("parque", "componente","estado","fecha")
    def __str__(self):
        return 'Plan, parque='+self.parque.nombre+',componente='+self.componente.nombre+',estado='+self.estado.nombre+\
               ',nº de aerogeneradores='+str(self.no_aerogeneradores)

@python_2_unicode_compatible
class Contractual(models.Model):
    parque = models.ForeignKey(ParqueSolar, on_delete=models.CASCADE)
    componente = models.ForeignKey(Componente, on_delete=models.CASCADE)
    estado = models.ForeignKey(EstadoFU, on_delete=models.CASCADE)
    fecha = models.DateField(blank=False, null=False)
    no_aerogeneradores = models.SmallIntegerField()
    class Meta:
        unique_together = ("parque", "componente","estado","fecha")
    def __str__(self):
        return 'Contractual, parque=' + self.parque.nombre + ',componente=' + self.componente.nombre + ',estado=' + self.estado.nombre + \
               ',nº de aerogeneradores=' + str(self.no_aerogeneradores)