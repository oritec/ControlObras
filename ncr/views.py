# -*- coding: utf-8 -*-
from django.shortcuts import render
from vista.functions import *
from django.contrib.auth.decorators import login_required, permission_required
from vista.models import ParqueSolar
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from forms import ObservacionForm, RevisionForm, RevisionFormFull
from ncr.models import Observacion, Revision, Fotos
from django.core import serializers
import json
import logging
import os
logger = logging.getLogger('oritec')

@login_required(login_url='ingresar')
def home(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Parque Eólico-NCR'
    contenido.subtitulo=parque.nombre
    contenido.menu = ['menu-principal', 'menu2-resumen']

    return render(request, 'vista/home.html',
        {'cont': contenido,
         'parque': parque,
        })

@login_required(login_url='ingresar')
def observaciones_resumen(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Resumen de Observaciones'
    contenido.subtitulo='Parque '+parque.nombre
    contenido.menu = ['menu-ncr', 'menu2-observaciones-resumen']
    observaciones = Observacion.objects.filter(parque=parque)
    url_append = ''
    table_show_ag = True
    return render(request, 'ncr/resumen.html',
                  {'cont': contenido,
                   'parque': parque,
                   'observaciones': observaciones,
                   'url_append':url_append,
                   'table_show_ag': table_show_ag,
                   })

@login_required(login_url='ingresar')
def observaciones(request,slug,ag_id):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'NCR Aerogenerador WTG'+str(ag_id).zfill(2)
    contenido.subtitulo='Parque '+ parque.nombre
    contenido.menu = ['menu-ncr', 'menu2-observaciones-'+str(ag_id)]
    url_append='?aerogenerador='+str(ag_id)

    observaciones = Observacion.objects.filter(aerogenerador__exact=ag_id, parque= parque)
    return render(request, 'ncr/resumen.html',
        {'cont': contenido,
         'parque': parque,
         'observaciones': observaciones,
         'url_append': url_append,
        })

@login_required(login_url='ingresar')
def add_observacion(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Agregar Observacion'
    contenido.subtitulo=parque.nombre
    if 'aerogenerador' in request.GET:
        contenido.menu = ['menu-ncr', 'menu2-observaciones-'+str(request.GET['aerogenerador'])]
        ag_readonly = True
        back_url = reverse('ncr:observaciones', args=[parque.slug,request.GET['aerogenerador']])
    else:
        contenido.menu = ['menu-ncr', 'menu2-observaciones-resumen']
        ag_readonly = False
        back_url = reverse('ncr:observaciones-resumen', args=[parque.slug])
    observacionForm = None

    #logger.debug(request.GET['aerogenerador'])

    if request.method == 'POST':
        observacionForm = ObservacionForm(request.POST,initial={"parque":parque})
        revisionForm = RevisionForm(request.POST)
        if observacionForm.is_valid() and revisionForm.is_valid():
            logger.debug('Formularios válidos.')
            observacion = observacionForm.save(commit=False)
            observacion.created_by = request.user
            observacion.save()
            revision = revisionForm.save(commit=False)
            revision.observacion = observacion
            revision.created_by = request.user
            revision.reported_by = observacion.reported_by
            revision.save()
            return HttpResponseRedirect(reverse('ncr:observaciones-show', args=[parque.slug,observacion.id]))
        else:
            logger.debug('Formulario no es válido...')

    if observacionForm is None:
        if 'aerogenerador' in request.GET:
            observacionForm = ObservacionForm(initial={"parque":parque,"aerogenerador":int(request.GET['aerogenerador'])})
        else:
            observacionForm = ObservacionForm(initial={"parque": parque})
        revisionForm = RevisionForm()

    return render(request, 'ncr/agregarObservacion.html',
        {'cont': contenido,
         'parque': parque,
         'observacionForm':observacionForm,
         'revisionForm': revisionForm,
         'ag_readonly': ag_readonly,
         'back_url': back_url,
        })

@login_required(login_url='ingresar')
def show_observacion(request,slug,observacion_id):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    observacion=get_object_or_404(Observacion, id=observacion_id)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Observación '
    contenido.subtitulo=parque.nombre
    contenido.menu = ['menu-ncr', 'menu2-observaciones-'+str(observacion.aerogenerador)]
    main_fotos = {}
    fotos = {}
    for r in observacion.revision_set.all():
        #logger.debug(r)
        fotos[r.id]=[]
        results = Fotos.objects.filter(revision=r,principal=True)
        if results.count() > 0:
            main_fotos[r.id]=results[0].thumbnail.url
        results = Fotos.objects.filter(revision=r)
        for foto in results:
            fotos[r.id].append(foto.imagen.url)

    return render(request, 'ncr/showObservacion.html',
        {'cont': contenido,
         'parque': parque,
         'observacion': observacion,
         'main_fotos': main_fotos,
         'fotos': fotos,
        })

@login_required(login_url='ingresar')
def add_images(request,slug,revision_id):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    revision= Revision.objects.get(pk=revision_id)
    logger.debug('Enter add_images')
    response_data = {}
    response_data['files'] = []
    if request.method == 'POST':
        for key, file in request.FILES.items():
            #logger.debug(file)
            primary = False
            instance = Fotos(imagen=file,revision=revision)
            instance.save()
            if request.POST['radio']==file.name:
                set_primary_photo(foto_id=instance.id)
                primary = True

            data={'name': file.name,
                  'size':str(file.size),
                  'url':instance.imagen.url,
                  'thumbnailUrl':instance.thumbnail.url,
                  'deleteUrl':reverse('ncr:imagenes-delete',args=[parque.slug,instance.id]),
                  "deleteType": "DELETE",
                  "mainPhoto": primary,
                  "photoId" : str(instance.id)}
            response_data['files'].append(data)
            #logger.debug(instance.imagen.url)
        response=json.dumps(response_data)

        return HttpResponse(
            response,
            content_type="application/json"
        )

@login_required(login_url='ingresar')
def list_fotos(request,slug):
    logger.debug("Enter list_fotos")
    parque = get_object_or_404(ParqueSolar, slug=slug)
    response_data = {}
    response_data['files'] = []
    if request.method == 'POST':
        revision = Revision.objects.get(pk=request.POST['revision_id'])
        results = Fotos.objects.filter(revision=revision)
        for foto in results:
            data={'name': os.path.basename(foto.imagen.name),
                  'size':str(foto.imagen.size),
                  'url':foto.imagen.url,
                  'thumbnailUrl':foto.thumbnail.url,
                  'deleteUrl':reverse('ncr:imagenes-delete',args=[parque.slug,foto.id]),
                  "deleteType": "DELETE",
                  "mainPhoto": foto.principal,
                  "photoId" : str(foto.id)}
            response_data['files'].append(data)
            #logger.debug(foto.imagen.url)
            #logger.debug(foto.principal)
            #logger.debug(foto.id)
        response=json.dumps(response_data)

        return HttpResponse(
            response,
            content_type="application/json"
        )

@login_required(login_url='ingresar')
def del_image(request,slug,image_id):
    logger.debug("Enter del_image")
    response_data = {}
    response_data['files'] = []
    if request.method == 'DELETE':
        foto = Fotos.objects.get(pk=image_id)
        foto.delete()
        data = {os.path.basename(foto.imagen.name):True}
        response_data['files'].append(data)
        response=json.dumps(response_data)

        return HttpResponse(
            response,
            content_type="application/json"
        )

def set_primary_photo(foto_id):
    foto = Fotos.objects.get(pk=foto_id)
    logger.debug("Enter set_primary_photo: " + foto.imagen.name)
    revision = foto.revision
    results = Fotos.objects.filter(revision=revision)
    for f in results:
        #logger.debug(f)
        f.principal = False
        f.save(update_fields=["principal"])
    foto.principal = True
    foto.save(update_fields=["principal"])

@login_required(login_url='ingresar')
def primary_image(request,slug):
    if request.method == 'POST':
        #logger.debug("post")
        set_primary_photo(foto_id=request.POST['foto_id'])
        foto = Fotos.objects.get(pk=request.POST['foto_id'])
        return HttpResponse(foto.thumbnail.url)

@login_required(login_url='ingresar')
def add_revision(request,slug,observacion_id):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Agregar Revisión'
    contenido.subtitulo=parque.nombre
    observacion = get_object_or_404(Observacion, id=observacion_id)
    contenido.menu = ['menu-ncr', 'menu2-observaciones-' + str(observacion.aerogenerador)]

    revisionForm = None

    if request.method == 'POST':
        revisionForm = RevisionFormFull(request.POST)
        if revisionForm.is_valid():
            logger.debug('Formulario válido.')
            revision = revisionForm.save(commit=False)
            revision.created_by = request.user
            revision.save()
            return HttpResponseRedirect(reverse('ncr:observaciones-show', args=[parque.slug,observacion.id]))
        else:
            logger.debug('Formulario no es válido...')

    if revisionForm is None:
        revisionForm = RevisionFormFull(initial={"observacion":observacion})

    return render(request, 'ncr/agregarRevision.html',
        {'cont': contenido,
         'parque': parque,
         'observacion': observacion,
         'revisionForm': revisionForm,
        })

@login_required(login_url='ingresar')
def informeNCR(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Informe NCR'
    contenido.subtitulo='Parque '+ parque.nombre
    contenido.menu = ['menu-ncr', 'menu2-informeNCR']


    return render(request, 'ncr/informeNCR.html',
        {'cont': contenido,
         'parque': parque,
        })

@login_required(login_url='ingresar')
def punchlist(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Punchlist'
    contenido.subtitulo='Parque '+ parque.nombre
    contenido.menu = ['menu-ncr', 'menu2-punchlist']


    return render(request, 'ncr/punchlist.html',
        {'cont': contenido,
         'parque': parque,
        })