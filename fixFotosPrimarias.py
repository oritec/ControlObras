# -*- coding: utf-8 -*-
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ControlObras.settings")
django.setup()

from ncr.models import Fotos,Revision

if __name__ == '__main__':

    revisiones = Revision.objects.all()
    for revision in revisiones:
        cuenta = 1
        fotos = Fotos.objects.filter(revision=revision, principal=True).order_by('-updated_at')
        for foto in fotos:
            foto.orden = cuenta
            foto.save(update_fields=["orden"])
            cuenta += 1
        fotos = Fotos.objects.filter(revision=revision, principal=False).order_by('-updated_at')
        for foto in fotos:
            foto.orden = cuenta
            foto.save(update_fields=["orden"])
            cuenta += 1

