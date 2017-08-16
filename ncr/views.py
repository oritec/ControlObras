# -*- coding: utf-8 -*-
from django.shortcuts import render
from vista.functions import *
from django.contrib.auth.decorators import login_required
from vista.models import ParqueSolar,Aerogenerador
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from forms import ObservacionForm, RevisionForm, RevisionFormFull, NCR, Punchlist
from ncr.models import Observacion, Revision, Fotos, Observador
from easy_pdf.rendering import render_to_pdf_response
import json
import logging
import os
import urlparse
logger = logging.getLogger('oritec')

@login_required(login_url='ingresar')
def home(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Parque Eólico-NCR'
    contenido.subtitulo=parque.nombre
    contenido.menu = ['menu-principal', 'menu2-resumen']

    return render(request, 'vista/home.html',
        {'cont': contenido,
         'parque': parque,
         'aerogeneradores':aerogeneradores,
        })

@login_required(login_url='ingresar')
def observaciones_resumen(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque)
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
                   'aerogeneradores':aerogeneradores,
                   })

@login_required(login_url='ingresar')
def observaciones(request,slug,ag_id):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque)
    aerogenerador = get_object_or_404(Aerogenerador,parque=parque,idx=ag_id)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'NCR Aerogenerador '+ aerogenerador.nombre
    contenido.subtitulo='Parque '+ parque.nombre
    contenido.menu = ['menu-ncr', 'menu2-observaciones-'+str(ag_id)]
    url_append='?aerogenerador='+str(ag_id)

    observaciones = Observacion.objects.filter(aerogenerador__idx__exact=ag_id, parque= parque)
    return render(request, 'ncr/resumen.html',
        {'cont': contenido,
         'parque': parque,
         'observaciones': observaciones,
         'url_append': url_append,
         'aerogeneradores':aerogeneradores,
        })

@login_required(login_url='ingresar')
def add_observacion(request,slug,observacion_id=0):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque)
    edit_observacion = None
    if observacion_id != 0:
        edit_observacion = get_object_or_404(Observacion,id=observacion_id)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.subtitulo=parque.nombre
    if 'aerogenerador' in request.GET:
        contenido.titulo = u'Agregar Observacion'
        contenido.menu = ['menu-ncr', 'menu2-observaciones-'+str(request.GET['aerogenerador'])]
        ag_readonly = True
        back_url = reverse('ncr:observaciones', args=[parque.slug,request.GET['aerogenerador']])
    elif edit_observacion is not None:
        contenido.titulo = u'Editar Observacion'
        contenido.menu = ['menu-ncr', 'menu2-observaciones-' + str(edit_observacion.aerogenerador.idx)]
        ag_readonly = False
        back_url = reverse('ncr:observaciones-show', args=[parque.slug, str(edit_observacion.id)])
    else:
        contenido.titulo = u'Agregar Observacion'
        contenido.menu = ['menu-ncr', 'menu2-observaciones-resumen']
        ag_readonly = False
        back_url = reverse('ncr:observaciones-resumen', args=[parque.slug])

    observacionForm = None

    #logger.debug(request.GET['aerogenerador'])

    if request.method == 'POST':
        if edit_observacion is not None:
            observacionForm = ObservacionForm(request.POST,instance=edit_observacion)
            rev = edit_observacion.revision_set.order_by('id')[0]
            revisionForm = RevisionForm(request.POST,instance=rev)
        else:
            observacionForm = ObservacionForm(request.POST,initial={"parque":parque})
            revisionForm = RevisionForm(request.POST)
        if observacionForm.is_valid() and revisionForm.is_valid():
            if edit_observacion is not None:
                observacion = observacionForm.save()
                revision = revisionForm.save()
            else:
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
        if edit_observacion is not None:
            observacionForm = ObservacionForm(instance=edit_observacion)
            rev = edit_observacion.revision_set.order_by('id')[0]
            revisionForm = RevisionForm(instance=rev)
        else:
            if 'aerogenerador' in request.GET:
                ag = get_object_or_404(Aerogenerador, idx=int(request.GET['aerogenerador']), parque=parque)
                observacionForm = ObservacionForm(initial={"parque":parque,"aerogenerador":ag.id})
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
         'aerogeneradores':aerogeneradores,
         'edit_observacion': edit_observacion,
        })

@login_required(login_url='ingresar')
def show_observacion(request,slug,observacion_id):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    observacion=get_object_or_404(Observacion, id=observacion_id)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Observación '
    contenido.subtitulo=parque.nombre
    contenido.menu = ['menu-ncr', 'menu2-observaciones-'+str(observacion.aerogenerador.idx)]
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
         'aerogeneradores':aerogeneradores
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
def add_revision(request,slug,observacion_id, revision_id = 0):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque)
    edit_revision = None
    if revision_id != 0:
        edit_revision = get_object_or_404(Revision, id=revision_id)
    contenido=ContenidoContainer()
    contenido.user=request.user
    if edit_revision is not None:
        contenido.titulo = u'Editar Revisión'
    else:
        contenido.titulo=u'Agregar Revisión'
    contenido.subtitulo=parque.nombre
    observacion = get_object_or_404(Observacion, id=observacion_id)
    contenido.menu = ['menu-ncr', 'menu2-observaciones-' + str(observacion.aerogenerador.idx)]

    revisionForm = None

    if request.method == 'POST':
        if edit_revision is not None:
            revisionForm = RevisionFormFull(request.POST, instance=edit_revision)
        else:
            revisionForm = RevisionFormFull(request.POST)
        if revisionForm.is_valid():
            logger.debug('Formulario válido.')
            if edit_revision is not None:
                revision = revisionForm.save()
            else:
                revision = revisionForm.save(commit=False)
                revision.created_by = request.user
                revision.save()
            revision.observacion.save() # Necesario para actualizar campos
            return HttpResponseRedirect(reverse('ncr:observaciones-show', args=[parque.slug,observacion.id]))
        else:
            logger.debug('Formulario no es válido...')

    if revisionForm is None:
        if edit_revision is not None:
            revisionForm = RevisionFormFull(instance=edit_revision)
        else:
            revisionForm = RevisionFormFull(initial={"observacion":observacion})

    return render(request, 'ncr/agregarRevision.html',
        {'cont': contenido,
         'parque': parque,
         'observacion': observacion,
         'revisionForm': revisionForm,
         'aerogeneradores':aerogeneradores,
         'edit_revision': edit_revision,
        })

@login_required(login_url='ingresar')
def informeNCR(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Informe NCR'
    contenido.subtitulo='Parque '+ parque.nombre
    contenido.menu = ['menu-ncr', 'menu2-informeNCR']

    form = NCR(parque=parque)
    resultados = None

    if request.method == 'POST':
        logger.debug('informeNCR Post')
        form = NCR(request.POST,parque=parque)
        if form.is_valid():
            logger.debug("Form Valid")
            resultados = Observacion.objects.filter(aerogenerador__in=form.cleaned_data['aerogenerador'])
            resultados = resultados.filter(estado__in=form.cleaned_data['estado'])
            resultados = resultados.filter(componente__in=form.cleaned_data['componente'])
            resultados = resultados.filter(sub_componente__in=form.cleaned_data['subcomponente'])
            resultados = resultados.filter(tipo__in=form.cleaned_data['tipo'])
            #for key,value in form.cleaned_data.iteritems():
            #    logger.debug(key)
            logger.debug(resultados)


    return render(request, 'ncr/informeNCR.html',
        {'cont': contenido,
         'parque': parque,
         'aerogeneradores':aerogeneradores,
         'form':form,
         'resultados':resultados,
        })

@login_required(login_url='ingresar')
def punchlist(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Punchlist'
    contenido.subtitulo='Parque '+ parque.nombre
    contenido.menu = ['menu-ncr', 'menu2-punchlist']

    form = Punchlist(parque=parque)
    resultados = None
    main_fotos = {}

    if request.method == 'POST':
        logger.debug('informePunchlist Post')
        form = Punchlist(request.POST, parque=parque)
        if form.is_valid():
            logger.debug("Form Valid")
            resultados = Observacion.objects.filter(aerogenerador__in=form.cleaned_data['aerogenerador'])
            # for key,value in form.cleaned_data.iteritems():
            #    logger.debug(key)
            for res in resultados:
                for r in res.revision_set.all().order_by('-id'):
                    results = Fotos.objects.filter(revision=r, principal=True)
                    if results.count() > 0:
                        main_fotos[r.id] = results[0].reporte_img.url
            logger.debug(resultados)
            respuesta=render_to_pdf_response(request,'ncr/punchlistPDF.html',
                                   {'pagesize':'LETTER',
                                    'title': 'Reporte Punchlist',
                                     'resultados':resultados,
                                    'main_fotos': main_fotos,
                                    'parque':parque
                                   }, content_type='application/pdf',
                                      response_class=HttpResponse )
            respuesta['Content-Disposition'] = 'attachment; filename="ReportePunchlist.pdf"'
            return respuesta
    return render(request, 'ncr/punchlist.html',
        {'cont': contenido,
         'parque': parque,
         'aerogeneradores':aerogeneradores,
         'form': form,
         'resultados': resultados,
        })

@login_required(login_url='ingresar')
def observadores(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Listado de observadores'
    contenido.subtitulo='Parque '+ parque.nombre
    contenido.menu = ['menu-principal', 'menu2-observadores']
    observadores = Observador.objects.all().order_by('id')
    response_data = {}

    # Me decido por interfaz RESTful. POST: Crear Nuevo, DELETE: Eliminar, PUT: Editar
    if request.method == 'POST':
        logger.debug('POST')
        editar = Observador.objects.get(id=int(request.POST['id']))
        editar.nombre = request.POST['nombre']
        editar.save()
        response_data['id'] = str(editar.id)
        response = json.dumps(response_data)
        return HttpResponse(
            response,
            content_type="application/json"
        )
    elif request.method == 'DELETE':
        #logger.debug('DELETE')
        data = dict(urlparse.parse_qsl(request.body))
        borrar = Observador.objects.get(id=data['id'])
        logger.debug("Borrando nombre=" +borrar.nombre)
        borrar.delete()
        return HttpResponse(
            '',
            content_type="application/json"
        )
    elif request.method == 'PUT':
        data=dict(urlparse.parse_qsl(request.body))
        nuevo = Observador(nombre = data['nombre'])
        nuevo.save()
        response_data['id'] = str(nuevo.id)
        response = json.dumps(response_data)
        return HttpResponse(
            response,
            content_type="application/json"
        )
    return render(request, 'ncr/agregarObservador.html',
        {'cont': contenido,
         'parque': parque,
         'observadores': observadores,
         'aerogeneradores':aerogeneradores,
        })

@login_required(login_url='ingresar')
def del_observacion(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Listado de observadores'
    contenido.subtitulo='Parque '+ parque.nombre
    contenido.menu = ['menu-principal', 'menu2-observadores']
    observadores = Observador.objects.all().order_by('id')
    response_data = {}

    if request.method == 'POST':
        logger.debug('POST del_observacion')
        Observacion.objects.get(id=int(request.POST['del_id'])).delete()
        return HttpResponseRedirect(request.POST['back_url'])

@login_required(login_url='ingresar')
def del_revision(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Listado de observadores'
    contenido.subtitulo='Parque '+ parque.nombre
    contenido.menu = ['menu-principal', 'menu2-observadores']
    observadores = Observador.objects.all().order_by('id')
    response_data = {}

    if request.method == 'POST':
        logger.debug('POST del_observacion')
        revision=Revision.objects.get(id=int(request.POST['del_id']))
        observacion = revision.observacion
        revision.delete()
        observacion.save()  # Necesario para actualizar campos
        return HttpResponseRedirect(request.POST['back_url'])

@login_required(login_url='ingresar')
def close_observacion(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Listado de observadores'
    contenido.subtitulo='Parque '+ parque.nombre
    contenido.menu = ['menu-principal', 'menu2-observadores']
    observadores = Observador.objects.all().order_by('id')
    response_data = {}

    if request.method == 'POST':
        logger.debug('POST del_observacion')
        observacion=Observacion.objects.get(id=int(request.POST['del_id']))
        if request.POST['cerrar'] == '1':
            observacion.msg_cerrado = request.POST['cierre_msg']
            observacion.cerrado = True
        else:
            observacion.msg_cerrado = ''
            observacion.cerrado = False
        observacion.save()
        return HttpResponseRedirect(request.POST['back_url'])