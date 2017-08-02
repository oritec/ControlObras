# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.template import defaultfilters
#from vista.models import ParqueSolar
import logging
logger = logging.getLogger('oritec')

@python_2_unicode_compatible
class Componente(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return '%s' % (self.nombre)

@python_2_unicode_compatible
class Subcomponente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return '%s' % (self.nombre)

@python_2_unicode_compatible
class Tipo(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return '%s' % (self.nombre)

@python_2_unicode_compatible
class Severidad(models.Model):
    nombre = models.CharField(max_length=2, unique=True)
    def __str__(self):
        return '%s' % (self.nombre)

@python_2_unicode_compatible
class EstadoRevision(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return '%s' % (self.nombre)

def rev_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'fotos/observacion_{0}/revision_{1}/{2}'.format(instance.revision.observacion.id, instance.revision.id, filename)

def thumbnails_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'thumbnails/observacion_{0}/revision_{1}/{2}'.format(instance.revision.observacion.id, instance.revision.id, filename)

class Fotos(models.Model):
    revision = models.ForeignKey('Revision', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to=rev_directory_path)
    thumbnail = models.ImageField(upload_to=thumbnails_directory_path,max_length=500, null=True, blank=True)
    principal = models.BooleanField(default=False)
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

        DJANGO_TYPE = self.imagen.file.content_type

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

    def save(self, *args, **kwargs):
        logger.debug("Saving Image")
        updateThumbnail = True
        if self.pk is not None:
            orig = Fotos.objects.get(pk=self.pk)
            if orig.imagen == self.imagen:
                updateThumbnail = False

        if updateThumbnail:
            logger.debug("Before create_thumbnail")
            self.create_thumbnail()
            logger.debug("After create_thumbnail")

        force_update = False

        # If the instance already has been saved, it has an id and we set
        # force_update to True
        if self.id:
            force_update = True

        # Force an UPDATE SQL query if we're editing the image to avoid integrity exception
        super(Fotos, self).save(force_update=force_update)


@python_2_unicode_compatible
class Observacion(models.Model):
    parque = models.ForeignKey('vista.ParqueSolar', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, unique=True)
    aerogenerador = models.IntegerField()
    fecha_observacion = models.DateField(blank=False,null=False)
    componente = models.ForeignKey('Componente', on_delete=models.SET_NULL, null=True)
    sub_componente = models.ForeignKey('Subcomponente', on_delete=models.SET_NULL, null=True)
    tipo = models.ForeignKey('Tipo', on_delete=models.SET_NULL, null=True)
    punchlist = models.BooleanField(default=False)
    estado = models.ForeignKey('EstadoRevision', on_delete=models.SET_NULL, null=True, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % (self.nombre)

@python_2_unicode_compatible
class Revision(models.Model):
    observacion = models.ForeignKey('Observacion', on_delete=models.CASCADE)
    fecha_revision = models.DateField(blank=False,null=False)
    severidad = models.ForeignKey('Severidad', on_delete=models.SET_NULL, null=True)
    descripcion = models.CharField(max_length=500)
    estado = models.ForeignKey('EstadoRevision', on_delete=models.SET_NULL, null=True, default =1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % (self.descripcion)