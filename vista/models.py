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

def logos_excel_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'logos/excel/{0}'.format(filename)

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
    logo_excel = models.ImageField(upload_to=logos_excel_directory_path, max_length=500, null=True, blank=True)
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

    def create_excel_logo(self):
        # original code for this method came from
        # http://snipt.net/danfreak/generate-thumbnails-in-django-with-pil/

        # If there is no image associated with this.
        # do not create thumbnail
        if not self.logo:
            return

        original_image = self.logo

        from PIL import Image
        from cStringIO import StringIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        import os

        # Set our max thumbnail size in a tuple (max width, max height)
        THUMBNAIL_SIZE = (800, 70)

        try:
            DJANGO_TYPE = original_image.file.content_type
        except Exception as e:
            if original_image.name.lower().endswith(".jpg"):
                DJANGO_TYPE = 'image/jpeg'
            elif original_image.name.lower().endswith(".png"):
                DJANGO_TYPE = 'image/png'
            elif original_image.name.lower().endswith(".JPG"):
                DJANGO_TYPE = 'image/jpeg'
            elif original_image.name.lower().endswith(".PNG"):
                DJANGO_TYPE = 'image/png'
            elif original_image.name.lower().endswith(".jpeg"):
                DJANGO_TYPE = 'image/jpeg'

        if DJANGO_TYPE == 'image/jpeg':
            PIL_TYPE = 'jpeg'
            FILE_EXTENSION = 'jpg'
        elif DJANGO_TYPE == 'image/png':
            PIL_TYPE = 'png'
            FILE_EXTENSION = 'png'

        # Open original photo which we want to thumbnail using PIL's Image
        image = Image.open(StringIO(original_image.read()))

        # We use our PIL Image object to create the thumbnail, which already
        # has a thumbnail() convenience method that contrains proportions.
        # Additionally, we use Image.ANTIALIAS to make the image look better.
        # Without antialiasing the image pattern artifacts may result.

        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
        #return 0
        # Save the thumbnail
        temp_handle = StringIO()
        image.save(temp_handle, PIL_TYPE)
        temp_handle.seek(0)

        # Save image to a SimpleUploadedFile which can be saved into
        # ImageField
        suf = SimpleUploadedFile(os.path.split(original_image.name)[-1],
                                 temp_handle.read(), content_type=DJANGO_TYPE)
        # Save SimpleUploadedFile into image field
        self.logo_excel.save(
            '%s_thumbnail.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
            suf,
            save=False
        )
        original_image.seek(0)

    def save(self, *args, **kwargs):
        self.slug = defaultfilters.slugify(self.codigo)

        updateThumbnail = True

        if self.pk is not None:
            orig = ParqueSolar.objects.get(pk=self.pk)
            if orig.logo == self.logo:
                updateThumbnail = False
            if self.logo_excel == '':
                updateThumbnail = True #Condicion inicial

        if updateThumbnail:
            try:
                self.create_excel_logo()
            except Exception as e:
                logger.debug(e.__doc__)
                logger.debug(e.message)

        force_update = False
        # self.create_reporte_img()
        # If the instance already has been saved, it has an id and we set
        # force_update to True
        if self.id:
            force_update = True

        # Force an UPDATE SQL query if we're editing the image to avoid integrity exception
        super(ParqueSolar, self).save(force_update=force_update)
