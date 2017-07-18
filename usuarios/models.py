from django.db import models

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

import logging
# Get an instance of a logger
logger = logging.getLogger('oritec')

# Dummy Model to create global permissions, a kind of helper.
class General(models.Model):
    dummy = models.PositiveIntegerField()

    class Meta:
        permissions = (
            ("vista", "Permiso de lectura"),
            ("revision", "Permiso de revision"),
            ("escritura", "Permiso para escribir"),
        )


class GlobalPermissionManager(models.Manager):
    def get_query_set(self):
        return super(GlobalPermissionManager, self).\
            get_query_set().filter(content_type__name='global_permission')

class GlobalPermission(Permission):
    """A global permission, not attached to a model"""
    objects = GlobalPermissionManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        ct, created = ContentType.objects.get_or_create(
            name="global_permission", app_label=self._meta.app_label
        )
        logger.debug(ct)
        self.content_type = ct
        super(GlobalPermission, self).save(*args, **kwargs)
        
class Usuario(models.Model):
    user = models.OneToOneField(User)
    foto=models.ImageField(upload_to='photos/%Y/%m/%d', null=True,blank=True,verbose_name=u'Foto')



