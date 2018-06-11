# -*- coding: utf-8 -*-
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ControlObras.settings")
django.setup()

from fu.models import ComponentesParque, Componente, EstadoFU, Membership, ParqueEolico, RelacionesFU
from vista.models import ParqueSolar

borrar = False

if __name__ == '__main__':
    parques = ParqueEolico.objects.all()
    no_parques = parques.count()

    if borrar:
        for parque in parques:
            parque.delete()

    if no_parques == 0: # Si el número de parques es cero, entonces hay que rellenar
        for c in ComponentesParque.objects.all():
            print(c.parque.nombre)
            parque_eolico = ParqueEolico(parque=c.parque)
            parque_eolico.save()
            # Iteramos para cada uno de los estados
            estado = EstadoFU.objects.get(nombre='Descarga')
            orden = 1
            for r in c.relacionesfu_set.filter(orden_descarga__gt=0).order_by('orden_descarga'):
                m = Membership(parque_eolico=parque_eolico,
                               componente=r.componente,
                               estado=estado,
                               orden=orden)
                m.save()
                orden += 1
            estado = EstadoFU.objects.get(nombre='Pre-Montaje')
            orden = 1
            for r in c.relacionesfu_set.filter(orden_premontaje__gt=0).order_by('orden_premontaje'):
                m = Membership(parque_eolico=parque_eolico,
                               componente=r.componente,
                               estado=estado,
                               orden=orden)
                m.save()
                orden += 1
            estado = EstadoFU.objects.get(nombre='Montaje')
            orden = 1
            for r in c.relacionesfu_set.filter(orden_montaje__gt=0).order_by('orden_montaje'):
                m = Membership(parque_eolico=parque_eolico,
                               componente=r.componente,
                               estado=estado,
                               orden=orden)
                m.save()
                orden += 1
            estado = EstadoFU.objects.get(nombre='Puesta en marcha')
            orden = 1
            for r in c.relacionesfu_set.filter(orden_puestaenmarcha__gt=0).order_by('orden_puestaenmarcha'):
                m = Membership(parque_eolico=parque_eolico,
                               componente=r.componente,
                               estado=estado,
                               orden=orden)
                m.save()
                orden += 1
    else:
        for p in parques:
            print(p.parque.nombre)
            for m in p.membership_set.all():
                print(' - ' + m.componente.nombre + ': ' + m.estado.nombre +'->'+ str(m.orden))






