# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from vista.models import Aerogenerador
from django.template import defaultfilters
#from vista.models import ParqueSolar
import logging

logger = logging.getLogger('oritec')


@python_2_unicode_compatible
class Observador(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return '%s' % (self.nombre)


@python_2_unicode_compatible
class Componente(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    orden_punchlist = models.IntegerField()

    def __str__(self):
        return '%s' % (self.nombre)
    def graphText(self):
        return '%s' % (self.nombre)

    def save(self, *args, **kwargs):
        if self.pk is None:
            aux = Componente.objects.all().order_by('orden_punchlist').last()
            if aux:
                self.orden_punchlist = aux.orden_punchlist + 1
        super(Componente, self).save()


@python_2_unicode_compatible
class Subcomponente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    # por legacy de componente
    orden_punchlist = models.IntegerField()
    def __str__(self):
        return '%s' % (self.nombre)
    def graphText(self):
        return '%s' % (self.nombre)
    def save(self, *args, **kwargs):
        if self.pk is None:
            aux = Subcomponente.objects.all().order_by('orden_punchlist').last()
            if aux:
                self.orden_punchlist = aux.orden_punchlist + 1
        super(Subcomponente, self).save()


@python_2_unicode_compatible
class Tipo(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    # por legacy de componente
    orden_punchlist = models.IntegerField()
    def __str__(self):
        return '%s' % (self.nombre)
    def graphText(self):
        return '%s' % (self.nombre)
    def save(self, *args, **kwargs):
        if self.pk is None:
            aux = Tipo.objects.all().order_by('orden_punchlist').last()
            if aux:
                self.orden_punchlist = aux.orden_punchlist + 1
        super(Tipo, self).save()


@python_2_unicode_compatible
class Severidad(models.Model):
    nombre = models.CharField(max_length=2, unique=True)
    def __str__(self):
        return '%s' % (self.nombre)
    def graphText(self):
        return 'Nivel ' + '%s' % (self.nombre)


@python_2_unicode_compatible
class EstadoRevision(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return '%s' % (self.nombre)
    def graphText(self):
        return '%s' % (self.nombre)


@python_2_unicode_compatible
class Prioridad(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    class Meta:
        ordering = ["id"]
    def graphText(self):
        return '%s' % (self.nombre)
    def __str__(self):
        return '%s' % (self.nombre)


def rev_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'fotos/parque_{0}/observacion_{1}/revision_{2}/{3}'.format(instance.revision.observacion.parque.id,
                                                                      instance.revision.observacion.id,
                                                                      instance.revision.id,
                                                                      filename)


def thumbnails_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'thumbnails/parque_{0}/observacion_{1}/revision_{2}/{3}'.format(instance.revision.observacion.parque.id,
                                                                           instance.revision.observacion.id,
                                                                           instance.revision.id,
                                                                           filename)


class Fotos(models.Model):
    revision = models.ForeignKey('Revision', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to=rev_directory_path)
    thumbnail = models.ImageField(upload_to=thumbnails_directory_path,max_length=500, null=True, blank=True)
    reporte_img = models.ImageField(upload_to=thumbnails_directory_path, null=True, blank=True)
    principal = models.BooleanField(default=False)
    orden = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def create_thumbnail(self):
        # original code for this method came from
        # http://snipt.net/danfreak/generate-thumbnails-in-django-with-pil/

        # If there is no image associated with this.
        # do not create thumbnail
        if not self.imagen:
            return

        from PIL import Image
        from cStringIO import StringIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        import os

        # Set our max thumbnail size in a tuple (max width, max height)
        THUMBNAIL_SIZE = (120, 120)

        try:
            DJANGO_TYPE = self.imagen.file.content_type
        except Exception as e:
            if self.imagen.name.lower().endswith(".jpg"):
                DJANGO_TYPE = 'image/jpeg'
            elif self.imagen.name.lower().endswith(".png"):
                DJANGO_TYPE = 'image/png'
            elif self.imagen.name.lower().endswith(".JPG"):
                DJANGO_TYPE = 'image/jpeg'
            elif self.imagen.name.lower().endswith(".PNG"):
                DJANGO_TYPE = 'image/png'

        if DJANGO_TYPE == 'image/jpeg':
            PIL_TYPE = 'jpeg'
            FILE_EXTENSION = 'jpg'
        elif DJANGO_TYPE == 'image/png':
            PIL_TYPE = 'png'
            FILE_EXTENSION = 'png'

        # Open original photo which we want to thumbnail using PIL's Image
        image = Image.open(StringIO(self.imagen.read()))

        # We use our PIL Image object to create the thumbnail, which already
        # has a thumbnail() convenience method that contrains proportions.
        # Additionally, we use Image.ANTIALIAS to make the image look better.
        # Without antialiasing the image pattern artifacts may result.
        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

        # Save the thumbnail
        temp_handle = StringIO()
        image.save(temp_handle, PIL_TYPE)
        temp_handle.seek(0)

        # Save image to a SimpleUploadedFile which can be saved into
        # ImageField
        suf = SimpleUploadedFile(os.path.split(self.imagen.name)[-1],
                                 temp_handle.read(), content_type=DJANGO_TYPE)
        # Save SimpleUploadedFile into image field
        self.thumbnail.save(
            '%s_thumbnail.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
            suf,
            save=False
        )
        self.imagen.seek(0)

    def create_reporte_img(self):
        # original code for this method came from
        # http://snipt.net/danfreak/generate-thumbnails-in-django-with-pil/

        # If there is no image associated with this.
        # do not create thumbnail
        if not self.imagen:
            return

        from PIL import Image
        from cStringIO import StringIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        import os

        # Set our max thumbnail size in a tuple (max width, max height)
        THUMBNAIL_SIZE = (650, 650)

        try:
            DJANGO_TYPE = self.imagen.file.content_type
        except Exception as e:
            if self.imagen.name.lower().endswith(".jpg"):
                DJANGO_TYPE = 'image/jpeg'
            elif self.imagen.name.lower().endswith(".png"):
                DJANGO_TYPE = 'image/png'
            elif self.imagen.name.lower().endswith(".JPG"):
                DJANGO_TYPE = 'image/jpeg'
            elif self.imagen.name.lower().endswith(".PNG"):
                DJANGO_TYPE = 'image/png'

        if DJANGO_TYPE == 'image/jpeg':
            PIL_TYPE = 'jpeg'
            FILE_EXTENSION = 'jpg'
        elif DJANGO_TYPE == 'image/png':
            PIL_TYPE = 'png'
            FILE_EXTENSION = 'png'

        # Open original photo which we want to thumbnail using PIL's Image
        image = Image.open(StringIO(self.imagen.read()))
        if image.width < image.height:
            image = image.transpose(Image.ROTATE_90)
        # We use our PIL Image object to create the thumbnail, which already
        # has a thumbnail() convenience method that contrains proportions.
        # Additionally, we use Image.ANTIALIAS to make the image look better.
        # Without antialiasing the image pattern artifacts may result.
        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

        # Save the thumbnail
        temp_handle = StringIO()
        image.save(temp_handle, PIL_TYPE)
        temp_handle.seek(0)

        # Save image to a SimpleUploadedFile which can be saved into
        # ImageField
        suf = SimpleUploadedFile(os.path.split(self.imagen.name)[-1],
                                 temp_handle.read(), content_type=DJANGO_TYPE)
        # Save SimpleUploadedFile into image field
        self.reporte_img.save(
            '%s_reporte.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
            suf,
            save=False
        )
        self.imagen.seek(0)

    def save(self, *args, **kwargs):
        # logger.debug("Saving Image")
        update_thumbnail = True
        if self.pk is not None:
            orig = Fotos.objects.get(pk=self.pk)
            if orig.imagen == self.imagen:
                update_thumbnail = False

        if update_thumbnail:
            try:
                self.create_thumbnail()
                self.create_reporte_img()
            except Exception as e:
                logger.debug(e.__doc__)
                logger.debug(e.message)

        force_update = False
        #self.create_reporte_img()
        # If the instance already has been saved, it has an id and we set
        # force_update to True
        if self.id:
            force_update = True

        # Force an UPDATE SQL query if we're editing the image to avoid integrity exception
        super(Fotos, self).save(force_update=force_update)


@python_2_unicode_compatible
class Observacion(models.Model):
    parque = models.ForeignKey('vista.ParqueSolar', on_delete=models.CASCADE)
    observacion_id = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, unique=False)
    aerogenerador = models.ForeignKey('vista.Aerogenerador', on_delete=models.SET_NULL, null=True)
    fecha_observacion = models.DateField(blank=False, null=False)
    componente = models.ForeignKey('Componente', on_delete=models.SET_NULL, null=True)
    sub_componente = models.ForeignKey('Subcomponente', on_delete=models.SET_NULL, null=True)
    tipo = models.ForeignKey('Tipo', on_delete=models.SET_NULL, null=True)
    punchlist = models.BooleanField(default=False)
    estado = models.ForeignKey('EstadoRevision', on_delete=models.SET_NULL, null=True, default=1)
    cerrado = models.BooleanField(default=False)  # False: No Cerrado, True:Cerrado
    msg_cerrado = models.CharField(max_length=500, blank=True, null=True, default='')
    clase = models.BooleanField(default=False)  # True: NCR, False: Sin Categoría (antes Incidencia)
    no_serie = models.CharField(max_length=100, unique=False, null=True, blank=True, default='')
    severidad = models.ForeignKey('Severidad', on_delete=models.SET_NULL, null=True)
    prioridad = models.ForeignKey('Prioridad', on_delete=models.SET_NULL, null=True)
    copied = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    reported_by = models.ForeignKey(Observador, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % self.nombre

    def save(self, *args, **kwargs):
        change_observacion_id = False
        if self.pk is None:
            change_observacion_id = True
        else:
            aux = self.__class__._default_manager.filter(pk=self.pk)
            if aux.count() > 0:
                last_aerogenerador = aux[0].aerogenerador
                if last_aerogenerador != self.aerogenerador:
                    change_observacion_id = True
        if self.observacion_id == 0:
            change_observacion_id = True

        if change_observacion_id:
            obs=Observacion.objects.filter(parque=self.parque, aerogenerador=self.aerogenerador).order_by('-observacion_id')
            if obs.count()>0:
                self.observacion_id = obs[0].observacion_id + 1
            else:
                self.observacion_id = 1

        aux = self.revision_set.filter(estado__nombre="Solucionado")
        res = self.revision_set.order_by('-id')

        if aux.count() > 0:
            self.estado = aux[0].estado
            self.severidad = aux[0].severidad
            self.prioridad = aux[0].prioridad
        elif res.count() > 0:
            aux2 = res[0]
            self.estado = aux2.estado
            self.severidad = aux2.severidad
            self.prioridad = aux2.prioridad

        super(Observacion, self).save(*args, **kwargs)  # Call the "real" save() method.


@python_2_unicode_compatible
class Revision(models.Model):
    observacion = models.ForeignKey('Observacion', on_delete=models.CASCADE)
    fecha_revision = models.DateField(blank=False,null=False)
    severidad = models.ForeignKey('Severidad', on_delete=models.SET_NULL, null=True)
    nombre = models.CharField(max_length=100, unique=False)
    descripcion = models.CharField(max_length=1000, blank=True, null=True)
    estado = models.ForeignKey('EstadoRevision', on_delete=models.SET_NULL, null=True, default=1)
    prioridad = models.ForeignKey('Prioridad', on_delete=models.SET_NULL, null=True, default=1)
    created_by = models.ForeignKey(User)
    reported_by = models.ForeignKey(Observador)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % self.descripcion