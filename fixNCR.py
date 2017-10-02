# -*- coding: utf-8 -*-
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ControlObras.settings")
django.setup()

from datetime import datetime,date

from vista.models import ParqueSolar, Aerogenerador
from fu.models import ComponentesParque, Componente, EstadoFU, Registros
from ncr.models import Revision,Observacion,Observador,Fotos
from django.contrib.auth.models import User
from django.core.files import File

if __name__ == '__main__':

    parque = ParqueSolar.objects.get(slug='cli-001')
    aerogenerador = Aerogenerador.objects.get(parque=parque, idx=1)
    user = User.objects.all().order_by('-id').last()
    observador = Observador.objects.get(id=2)

    fotosDict={}
    # traverse root directory, and list directories as dirs and files as files
    for root, dirs, files in os.walk("media/fotos2/"):
        path = root.split(os.sep)
        for file in files:
            if len(path) > 3:
                obs_id = int(path[2].split('_')[1])
                rev_id = int(path[3].split('_')[1])

                if obs_id >=7:
                    print 'Observacion id=' + str(obs_id) +', Revision id=' + str(rev_id)
                    obs = None
                    rev = None
                    try:
                        obs=Observacion.objects.get(id=obs_id)
                    except Observacion.DoesNotExist:
                        print 'No existe Observacion id='+str(obs_id)
                    try:
                        rev = Revision.objects.get(id=rev_id)
                    except Revision.DoesNotExist:
                        print 'No existe Revisión id='+str(rev_id)

                    if obs is None:
                        obs = Observacion(id=obs_id,
                                          parque=parque,
                                          aerogenerador=aerogenerador,
                                          fecha_observacion=date.today(),
                                          created_by = user,
                                          reported_by=observador)
                        obs.save()
                    if rev is None:
                        rev = Revision(id=rev_id,
                                       observacion=obs,
                                       created_by=user,
                                       fecha_revision=date.today(),
                                       reported_by=observador)
                        rev.save()
                    print(len(path) * '---', file)
                    primary = True

                    filename = 'fotos2/observacion_'+str(obs_id)+'/revision_'+str(rev_id)+'/'+file
                    filename_real ='./media/'+filename
                    fotos = Fotos.objects.filter(revision=rev)
                    if fotos.count() > 0:
                        primary = False

                    foto = Fotos(revision=rev,principal=primary)
                    foto.imagen.save(file,File(open(filename_real)))
                    foto.save()