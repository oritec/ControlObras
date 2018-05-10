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
    descripcion = models.CharField(max_length=1000, unique=False)
    dr = models.ForeignKey('DR', on_delete=models.CASCADE)
    orden = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return '%s' % (self.descripcion)

@python_2_unicode_compatible
class ComposicionDR(models.Model):
    actividad = models.ForeignKey('ActividadDR', on_delete=models.CASCADE)
    pie = models.CharField(max_length=200, unique=False)
    tipo = models.CharField(max_length=10, unique=False)
    orden = models.SmallIntegerField(default=0)
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
        if image.height > 1200 or image.width >1200:
            THUMBNAIL_SIZE = (image.width*0.2, image.height*0.2)

        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
        #return 0
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

    def __str__(self):
        return '%s' % (self.descripcion)

    def save(self, *args, **kwargs):
        #logger.debug("Saving Image")
        updateThumbnail = True
        if self.pk is not None:
            orig = FotosDR.objects.get(pk=self.pk)
            if orig.imagen == self.imagen:
                updateThumbnail = False

        if updateThumbnail:
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
        super(FotosDR, self).save(force_update=force_update)