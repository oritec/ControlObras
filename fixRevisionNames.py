# -*- coding: utf-8 -*-
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ControlObras.settings")
django.setup()

from ncr.models import Revision

if __name__ == '__main__':

    revisiones = Revision.objects.all()
    for revision in revisiones:
        if revision.nombre == '':
            revision.nombre = revision.observacion.nombre
            revision.save()

