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
    reporte_img = models.ImageField(upload_to=thumbnails_directory_path, null=True, blank=True)
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
        #logger.debug("Saving Image")
        updateThumbnail = True
        if self.pk is not None:
            orig = Fotos.objects.get(pk=self.pk)
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
        super(Fotos, self).save(force_update=force_update)


@python_2_unicode_compatible
class Observacion(models.Model):
    parque = models.ForeignKey('vista.ParqueSolar', on_delete=models.CASCADE)
    observacion_id = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, unique=False)
    aerogenerador = models.ForeignKey('vista.Aerogenerador', on_delete=models.SET_NULL,null=True)
    fecha_observacion = models.DateField(blank=False,null=False)
    componente = models.ForeignKey('Componente', on_delete=models.SET_NULL, null=True)
    sub_componente = models.ForeignKey('Subcomponente', on_delete=models.SET_NULL, null=True)
    tipo = models.ForeignKey('Tipo', on_delete=models.SET_NULL, null=True)
    punchlist = models.BooleanField(default=False)
    estado = models.ForeignKey('EstadoRevision', on_delete=models.SET_NULL, null=True, default=1)
    cerrado = models.BooleanField(default=False)  # False: No Cerrado, True:Cerrado
    msg_cerrado = models.CharField(max_length=500, blank = True, null= True, default='')
    clase = models.BooleanField(default=True) # True: NCR, False:Incidencia
    no_serie = models.CharField(max_length=100, unique=False,null=True,blank=True,default='')
    severidad = models.ForeignKey('Severidad', on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(User)
    reported_by = models.ForeignKey(Observador)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % (self.nombre)

    def save(self, *args, **kwargs):
        if self.pk is None or self.observacion_id == 0:
            obs=Observacion.objects.filter(parque=self.parque, aerogenerador=self.aerogenerador).order_by('-observacion_id')
            if obs.count()>0:
                self.observacion_id = obs[0].observacion_id + 1
            else:
                self.observacion_id = 1

        aux = self.revision_set.filter(estado__nombre="Solucionado")
        res = self.revision_set.order_by('-id')

        if aux.count() > 0:
            self.estado = aux[0].estado
        elif res.count() > 0:
            aux2 = res[0]
            self.estado = aux2.estado
            self.severidad = aux2.severidad

        super(Observacion, self).save(*args, **kwargs)  # Call the "real" save() method.

@python_2_unicode_compatible
class Revision(models.Model):
    observacion = models.ForeignKey('Observacion', on_delete=models.CASCADE)
    fecha_revision = models.DateField(blank=False,null=False)
    severidad = models.ForeignKey('Severidad', on_delete=models.SET_NULL, null=True)
    descripcion = models.CharField(max_length=500)
    estado = models.ForeignKey('EstadoRevision', on_delete=models.SET_NULL, null=True, default =1)
    created_by = models.ForeignKey(User)
    reported_by = models.ForeignKey(Observador)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % (self.descripcion)