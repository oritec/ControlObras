# -*- coding: utf-8 -*-
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ControlObras.settings")
django.setup()

from ncr.models import Observacion, Observador, Revision, Fotos

if __name__ == '__main__':
    # sarco = ParqueSolar.objects.get(slug='mst-0022')
    # observaciones = Observacion.objects.filter(parque=sarco).order_by('id')
    andres = Observador.objects.filter(id=5)
    observadores = Observador.objects.all()
    lista_observadores = list()
    for observador in Observador.objects.using('backup').all().order_by('id'):
        if observador not in observadores:
            print('No se encuentra observador id = ' + str(observador.id) + ', nombre = ' + observador.nombre)
            lista_observadores.append(observador)

    cuenta_parque = dict()
    lista_observaciones = list()
    observaciones = Observacion.objects.all().order_by('id')
    for observacion in Observacion.objects.using('backup').filter(reported_by__in=lista_observadores):
        if observacion not in observaciones:
            observacion.reported_by = None
            lista_observaciones.append(observacion)
            if observacion.parque.nombre not in cuenta_parque:
                cuenta_parque[observacion.parque.nombre] = 1
            else:
                cuenta_parque[observacion.parque.nombre] += 1

    cuenta_total = 0

    for key, cuenta in cuenta_parque.items():
        print(key + ': ' + str(cuenta))
        cuenta_total += cuenta

    print('total: ' + str(cuenta_total))

    for observacion in lista_observaciones:
        print(observacion.nombre)
        lista_revisiones = list()
        for revision in observacion.revision_set.all():
            lista_revisiones.append(revision)
        observacion_dict = observacion.__dict__
        for k in observacion_dict.keys():
            if k.startswith('_'):
                observacion_dict.pop(k)
        new_obs = Observacion.objects.using('default').create(**observacion_dict)
        for revision in lista_revisiones:
            lista_fotos = list()
            for foto in revision.fotos_set.all():
                lista_fotos.append(foto)
            revision.observacion.id = new_obs.id
            revision.reported_by = None
            revision_dict = revision.__dict__
            for k in revision_dict.keys():
                if k.startswith('_'):
                    revision_dict.pop(k)
            new_rev = Revision.objects.using('default').create(**revision_dict)
            for foto in lista_fotos:
                foto.revision.id = new_rev.id
                foto.id = None
                foto_dict = foto.__dict__
                for k in foto_dict.keys():
                    if k.startswith('_'):
                        foto_dict.pop(k)
                Fotos.objects.using('default').create(**foto_dict)
