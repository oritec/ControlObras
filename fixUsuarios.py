# -*- coding: utf-8 -*-
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ControlObras.settings")
django.setup()

from vista.models import ParqueSolar, Aerogenerador
from django.contrib.auth.models import User
from usuarios.models import Usuario


if __name__ == '__main__':

    usuarios_django = User.objects.all()
    for usuario_django in usuarios_django:
        if usuario_django.is_superuser:
            n=Usuario.objects.filter(user=usuario_django).count()
            if n == 0:
                usuario_sistema = Usuario(user=usuario_django)
                usuario_sistema.save()
                for parque in ParqueSolar.objects.all():
                    usuario_sistema.parques.add(parque)
                usuario_sistema.save()
        else:
            n = Usuario.objects.filter(user=usuario_django).count()
            if n == 0:
                usuario_sistema = Usuario(user=usuario_django)
                usuario_sistema.save()




