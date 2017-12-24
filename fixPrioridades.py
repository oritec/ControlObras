# -*- coding: utf-8 -*-
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ControlObras.settings")
django.setup()

from ncr.models import Observacion

if __name__ == '__main__':
    for o in Observacion.objects.all():
        o.save()