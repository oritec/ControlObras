# -*- coding: utf-8 -*-
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ControlObras.settings")
django.setup()


from fu.models import Paradas


if __name__ == '__main__':
    paradas = Paradas.objects.all()
    for parada in paradas:
        if parada.viento is None:
            parada.motivo = ''
        else:
            parada.motivo = str(parada.viento)
        parada.save()




