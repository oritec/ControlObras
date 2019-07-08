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
    orden = models.IntegerField(default=0)

    def __str__(self):
        return '%s' % self.nombre


@python_2_unicode_compatible
class SectorObraElectrica(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    idx = models.IntegerField(unique=True)
    orden = models.IntegerField(default=0)

    def __str__(self):
        return '%s' % self.nombre


@python_2_unicode_compatible
class ComponenteObraElectrica(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    sectores = models.ManyToManyField(SectorObraElectrica)

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
    componentes_obraelectrica = models.ManyToManyField(ComponenteObraElectrica,
                                                       through='MembershipObraElectrica',
                                                       related_name='members_electricos')

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
class MembershipObraElectrica(models.Model):
    parque_eolico = models.ForeignKey(ParqueEolico, on_delete=models.CASCADE)
    componente = models.ForeignKey(ComponenteObraElectrica, on_delete=models.CASCADE)
    sector = models.ForeignKey(SectorObraElectrica, on_delete=models.CASCADE)
    orden = models.SmallIntegerField()

    class Meta:
        unique_together = ("parque_eolico", "componente", "sector")

    def __str__(self):
        return 'Relacion Componente - Parque ' + '%s-%s' % (self.parque_eolico, self.componente.nombre)

    def save(self, *args, **kwargs):
        if self.pk is None:
            aux = MembershipObraElectrica.objects.filter(parque_eolico=self.parque_eolico,
                                                         sector=self.sector).order_by('-orden')
            if aux.count() == 0:
                self.orden = 1
            else:
                last = aux[0]
                self.orden = last.orden + 1
        super(MembershipObraElectrica, self).save()


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
    componente_montaje = models.ForeignKey(Componente, null=True, default=None, blank=True, on_delete=models.SET_NULL)

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
class PlanObrasElectricas(models.Model):
    parque = models.ForeignKey(ParqueSolar, on_delete=models.CASCADE)
    componente = models.ForeignKey(ComponenteObraElectrica, on_delete=models.CASCADE)
    sector = models.ForeignKey(SectorObraElectrica, on_delete=models.CASCADE)
    fecha = models.DateField(blank=False, null=False)
    avance = models.FloatField()

    class Meta:
        unique_together = ("parque", "componente", "sector", "fecha")

    def __str__(self):
        return 'Plan Obras Civiles, parque=' + self.parque.nombre + \
               ',componente=' + self.componente.nombre + \
               ',sector=' + self.sector.nombre + \
               ',avance=' + str(self.avance)


@python_2_unicode_compatible
class ContractualObrasElectricas(models.Model):
    parque = models.ForeignKey(ParqueSolar, on_delete=models.CASCADE)
    componente = models.ForeignKey(ComponenteObraElectrica, on_delete=models.CASCADE)
    sector = models.ForeignKey(SectorObraElectrica, on_delete=models.CASCADE)
    fecha = models.DateField(blank=False, null=False)
    avance = models.FloatField()

    class Meta:
        unique_together = ("parque", "componente", "sector", "fecha")

    def __str__(self):
        return 'Contractual Obras Civiles, parque=' + self.parque.nombre + \
               ',componente=' + self.componente.nombre + \
               ',sector=' + self.sector.nombre + \
               ',avance=' + str(self.avance)


@python_2_unicode_compatible
class Registros(models.Model):
    parque = models.ForeignKey(ParqueSolar, on_delete=models.CASCADE)
    aerogenerador = models.ForeignKey(Aerogenerador, on_delete=models.CASCADE)
    componente = models.ForeignKey(Componente, on_delete=models.CASCADE)
    estado = models.ForeignKey(EstadoFU, on_delete=models.CASCADE)
    fecha = models.DateField(blank=False, null=False)
    no_serie = models.CharField(max_length=100, unique=False, blank=False, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ("parque", "aerogenerador", "componente", "estado")

    def __str__(self):
        return 'Registro, parque=' + self.parque.nombre + ',aerogenerador=' + self.aerogenerador.nombre + \
               ',componente=' + self.componente.nombre + ',estado=' + self.estado.nombre + \
               ',fecha=' + self.fecha.strftime("%d-%m-%Y")


@python_2_unicode_compatible
class RegistrosObraElectrica(models.Model):
    AVANCE_OPCIONES = [
        (0, '0%'),
        (25, '25%'),
        (50, '50%'),
        (75, '75%'),
        (100, '100%'),
    ]
    parque = models.ForeignKey(ParqueSolar, on_delete=models.CASCADE)
    componente = models.ForeignKey(ComponenteObraElectrica, on_delete=models.CASCADE)
    sector = models.ForeignKey(SectorObraElectrica, on_delete=models.CASCADE)
    fecha = models.DateField(blank=False, null=False)
    avance = models.IntegerField(default=0, choices=AVANCE_OPCIONES)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Registro Obra Eléctrica, parque=' + self.parque.nombre + \
               ',componente=' + self.componente.nombre + ', sector=' + self.sector.nombre + \
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
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return 'Paradas, parque=' + self.parque.nombre + ',aerogenerador=' + self.aerogenerador.nombre + \
               ',componente=' + self.componente.nombre + ',fecha_inicial=' + self.fecha_inicial.strftime("%d-%m-%Y") + \
               ',fecha_final=' + self.fecha_final.strftime("%d-%m-%Y")

    def save(self, *args, **kwargs):
        if self.fecha_inicio and self.fecha_final:
            c = self.fecha_final - self.fecha_inicio
            self.duracion = c.total_seconds()/3600
        super(Paradas, self).save(*args, **kwargs)  # Call the "real" save() method.


def caminos_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'caminos/{0}'.format(filename)


@python_2_unicode_compatible
class Camino(models.Model):
    parque = models.ForeignKey(ParqueSolar, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, unique=True)
    orden = models.IntegerField(default=0)
    imagen = models.FileField(upload_to=caminos_directory_path, max_length=500, null=True, blank=True)

    class Meta:
        unique_together = ("parque", "nombre")

    def __str__(self):
        return '%s' % self.nombre

    def save(self, *args, **kwargs):
        if self.orden == 0:
            last_orden = Camino.objects.filter(parque=self.parque).order_by('orden').last()
            if last_orden:
                self.orden = last_orden.orden + 1
            else:
                self.orden = 1
        super(Camino, self).save(*args, **kwargs)


@python_2_unicode_compatible
class PlanCaminos(models.Model):
    parque = models.ForeignKey(ParqueSolar, on_delete=models.CASCADE)
    componente = models.ForeignKey(Camino, on_delete=models.CASCADE)
    fecha = models.DateField(blank=False, null=False)
    avance = models.FloatField()

    class Meta:
        unique_together = ("parque", "componente", "fecha")

    def __str__(self):
        return 'Plan Caminos, parque=' + self.parque.nombre + \
               ',componente=' + self.componente.nombre + \
               ',avance=' + str(self.avance)


@python_2_unicode_compatible
class ContractualCaminos(models.Model):
    parque = models.ForeignKey(ParqueSolar, on_delete=models.CASCADE)
    componente = models.ForeignKey(Camino, on_delete=models.CASCADE)
    fecha = models.DateField(blank=False, null=False)
    avance = models.FloatField()

    class Meta:
        unique_together = ("parque", "componente", "fecha")

    def __str__(self):
        return 'Contractual Caminos, parque=' + self.parque.nombre + \
               ',componente=' + self.componente.nombre + \
               ',avance=' + str(self.avance)


@python_2_unicode_compatible
class CaminoImagenAvance(models.Model):
    camino = models.ForeignKey(Camino, on_delete=models.CASCADE)
    imagen = models.FileField(upload_to=caminos_directory_path, max_length=500, null=True, blank=True)
    avance = models.IntegerField(default=0, choices=RegistrosObraElectrica.AVANCE_OPCIONES)

    class Meta:
        unique_together = ("camino", "avance")

    def __str__(self):
        return 'Imagen avance camino'


@python_2_unicode_compatible
class ObraElectricaImagenAvance(models.Model):
    parque_eolico = models.ForeignKey(ParqueEolico, on_delete=models.CASCADE)
    componente = models.ForeignKey(ComponenteObraElectrica, on_delete=models.CASCADE)
    imagen = models.FileField(upload_to=caminos_directory_path, max_length=500, null=True, blank=True)
    avance = models.IntegerField(default=0, choices=RegistrosObraElectrica.AVANCE_OPCIONES)

    class Meta:
        unique_together = ("parque_eolico", "componente", "avance")

    def __str__(self):
        return 'Imagen avance obra eléctrica'


@python_2_unicode_compatible
class RegistrosCamino(models.Model):
    parque = models.ForeignKey(ParqueSolar, on_delete=models.CASCADE)
    camino = models.ForeignKey(Camino, on_delete=models.CASCADE)
    fecha = models.DateField(blank=False, null=False)
    avance = models.IntegerField(default=0, choices=RegistrosObraElectrica.AVANCE_OPCIONES)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Registro Camino, parque=' + self.parque.nombre + \
               ',camino=' + self.camino.nombre + \
               ',fecha=' + self.fecha.strftime("%d-%m-%Y")
