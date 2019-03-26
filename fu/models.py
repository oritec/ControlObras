# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from vista.models import ParqueSolar,Aerogenerador
from django.contrib.auth.models import User
import datetime

import logging
logger = logging.getLogger('oritec')


@python_2_unicode_compatible
class EstadoFU(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    idx = models.IntegerField(unique=True)

    def __str__(self):
        return '%s' % self.nombre


@python_2_unicode_compatible
class Componente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    estados = models.ManyToManyField(EstadoFU)

    def __str__(self):
        return '%s' % self.nombre


@python_2_unicode_compatible
class ComponentesParque(models.Model):
    parque = models.OneToOneField(ParqueSolar, on_delete=models.CASCADE)
    componentes = models.ManyToManyField(Componente,
                                         through='RelacionesFU', through_fields=('componentes_parque', 'componente'))

    def __str__(self):
        return 'Componentes Parque ' + '%s' % self.parque.nombre


# Hay un evidente problema de nombre. ParqueSolar es un legacy name, que no tiene significado.
@python_2_unicode_compatible
class ParqueEolico(models.Model):
    parque = models.ForeignKey(ParqueSolar, on_delete=models.CASCADE)
    componentes = models.ManyToManyField(Componente, through='Membership', related_name='members')

    def __str__(self):
        return 'Componentes Parque Eolico' + '%s' % self.parque.nombre


@python_2_unicode_compatible
class Membership(models.Model):
    parque_eolico = models.ForeignKey(ParqueEolico, on_delete=models.CASCADE)
    componente = models.ForeignKey(Componente, on_delete=models.CASCADE)
    estado = models.ForeignKey(EstadoFU, on_delete=models.CASCADE)
    orden = models.SmallIntegerField()

    class Meta:
        unique_together = ("parque_eolico", "componente", "estado")

    def __str__(self):
        return 'Relacion Componente - Parque ' + '%s-%s' % (self.parque_eolico, self.componente.nombre)

    def save(self, *args, **kwargs):
        if self.pk is None:
            aux = Membership.objects.filter(parque_eolico=self.parque_eolico, estado=self.estado).order_by('-orden')
            if aux.count() == 0:
                self.orden = 1
            else:
                last = aux[0]
                self.orden = last.orden + 1
        super(Membership, self).save()


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
        return 'Relaciones Componentes Parque ' + '%s' % self.componentes_parque.parque.nombre


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
        unique_together = ("parque", "componente" ,"estado", "fecha")

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
        unique_together = ("parque", "componente", "estado", "fecha")

    def __str__(self):
        return 'Contractual, parque=' + \
               self.parque.nombre + \
               ',componente=' + self.componente.nombre + ',estado=' + self.estado.nombre + \
               ',nº de aerogeneradores=' + str(self.no_aerogeneradores)


@python_2_unicode_compatible
class Registros(models.Model):
    parque = models.ForeignKey(ParqueSolar, on_delete=models.CASCADE)
    aerogenerador = models.ForeignKey(Aerogenerador, on_delete=models.CASCADE)
    componente = models.ForeignKey(Componente, on_delete=models.CASCADE)
    estado = models.ForeignKey(EstadoFU, on_delete=models.CASCADE)
    fecha = models.DateField(blank=False, null=False)
    no_serie = models.CharField(max_length=100, unique=False, blank=False, null=True)
    created_by = models.ForeignKey(User)

    class Meta:
        unique_together = ("parque", "aerogenerador", "componente", "estado")

    def __str__(self):
        return 'Registro, parque=' + self.parque.nombre + ',aerogenerador=' + self.aerogenerador.nombre + \
               ',componente=' + self.componente.nombre + ',estado=' + self.estado.nombre + \
               ',fecha=' + self.fecha.strftime("%d-%m-%Y")


@python_2_unicode_compatible
class ParadasTrabajo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return '%s' % self.nombre


@python_2_unicode_compatible
class ParadasGrua(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return '%s' % self.nombre


@python_2_unicode_compatible
class Paradas(models.Model):
    parque = models.ForeignKey(ParqueSolar, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(blank=False, null=False)
    fecha_final = models.DateTimeField(blank=False, null=False)
    aerogenerador = models.ForeignKey(Aerogenerador,on_delete=models.CASCADE)
    componente = models.ForeignKey(Componente, on_delete=models.CASCADE, blank=True, null=True)
    trabajo = models.ForeignKey(ParadasTrabajo, on_delete=models.CASCADE)
    duracion = models.FloatField(blank=True,null=True)
    viento = models.FloatField(blank=True,null=True)
    motivo = models.CharField(max_length=200,blank=True,null=True, default='')
    grua = models.ForeignKey(ParadasGrua, on_delete=models.CASCADE, blank=True, null=True)
    observaciones = models.CharField(max_length=200,blank=True,null=True)
    created_by = models.ForeignKey(User)

    def __str__(self):
        return 'Paradas, parque=' + self.parque.nombre + ',aerogenerador=' + self.aerogenerador.nombre + \
               ',componente=' + self.componente.nombre + ',fecha_inicial=' + self.fecha_inicial.strftime("%d-%m-%Y") + \
               ',fecha_final=' + self.fecha_final.strftime("%d-%m-%Y")

    def save(self, *args, **kwargs):
        if self.fecha_inicio and self.fecha_final:
            c = self.fecha_final - self.fecha_inicio
            self.duracion = c.total_seconds()/3600
        super(Paradas, self).save(*args, **kwargs)  # Call the "real" save() method.
