# -*- coding: utf-8 -*-
from django.template.response import TemplateResponse
from vista.functions import *
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from forms import ParqueForm, ParqueFormFull
from models import ParqueSolar, Aerogenerador
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
import json
import logging
from django.db import IntegrityError
from usuarios.views import check_password, check_permisos
from usuarios.models import Usuario, Log
logger = logging.getLogger('oritec')


@login_required(login_url='ingresar')
def index(request):
    usuario = Usuario.objects.get(user=request.user)
    parques = usuario.parques.all()
    form_add_parque = ParqueForm()
    if request.method == 'POST':
        if 'addParque' in request.POST:
            form_parque = ParqueForm(request.POST)
            if form_parque.is_valid():
                p = form_parque.save()
                usuarios = Usuario.objects.all()
                for u in usuarios:
                    if u.user.is_superuser:
                        u.parques.add(p)
                usuario.parques.add(p)
                log_msg = "Se crea parque " + p.nombre
                log = Log(texto=log_msg, tipo=1, user=request.user)
                log.save()
            else:
                logger.debug('error')
                mensaje = 'Código de parque ya existe!'
                messages.add_message(request, messages.ERROR, mensaje)
    return TemplateResponse(request, 'vista/index.html',
                            {'parques': parques,
                                'formAddParque': form_add_parque,
                                'user': request.user
                             })


@login_required(login_url='ingresar')
def home(request, slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    ags = Aerogenerador.objects.filter(parque=parque)
    contenido = ContenidoContainer()
    contenido.user = request.user
    contenido.titulo = u'Parque Eólico'
    contenido.subtitulo = parque.nombre
    contenido.menu = ['menu-principal', 'menu2-resumen']

    return TemplateResponse(request, 'vista/home.html',
                            {'cont': contenido,
                                'parque': parque,
                                'aerogeneradores': ags
                             })


@login_required(login_url='ingresar')
@permission_required('vista.delete_parquesolar', raise_exception=True)
def del_parque(request):
    if request.method == 'POST':
        if 'parque' in request.POST:
            aux = ParqueSolar.objects.get(slug__exact=request.POST['parque'])
            log_msg = "Se elimina parque " + aux.nombre
            aux.delete()
            log = Log(texto=log_msg, tipo=3, user=request.user)
            log.save()
    return HttpResponseRedirect(reverse('vista:index'))


@login_required(login_url='ingresar')
@permission_required('vista.change_parquesolar', raise_exception=True)
def configuracion(request, slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque)
    contenido = ContenidoContainer()
    contenido.user=request.user
    contenido.titulo = u'Parque Eólico'
    contenido.subtitulo = parque.nombre
    contenido.menu = ['menu-principal', 'menu2-configuracion']
    form = None
    if request.method == 'POST':
        form = ParqueFormFull(request.POST, request.FILES, instance=parque)
        if form.is_valid():
            logger.debug("Formulario es válido")
            parque = form.save()
            log_msg = "Se cambia configuración de parque " + parque.nombre
            log = Log(texto=log_msg, tipo=2, user=request.user)
            log.save()
            mensaje = 'Información modificada con éxito'
            messages.add_message(request, messages.SUCCESS, mensaje)
            response = redirect('vista:home', slug=parque.slug)
            if parque.prev_no_aerogeneradores != parque.no_aerogeneradores:
                logger.debug('Se debe actualizar tabla de Aerogeneradores.')
                if parque.prev_no_aerogeneradores < parque.no_aerogeneradores:
                    ag = Aerogenerador.objects.filter(parque=parque, idx__gt=0).order_by('-idx')
                    last_idx = 0
                    if ag.count() > 0:
                        ultimo = ag[0]
                        last_idx = ag[0].idx
                    for idx in range(last_idx+1, parque.no_aerogeneradores+1):
                        nuevo = Aerogenerador(parque=parque, idx=idx, nombre='WTG'+str(idx).zfill(2))
                        nuevo.save()
                else:
                    Aerogenerador.objects.filter(parque=parque, idx__gt=parque.no_aerogeneradores)
                parque.prev_no_aerogeneradores = parque.no_aerogeneradores
            ag = Aerogenerador.objects.filter(parque=parque, idx=-1)
            if ag.count() == 0:
                nuevo = Aerogenerador(parque=parque, idx=-2, nombre='General')
                nuevo.save()
                nuevo = Aerogenerador(parque=parque, idx=-1, nombre='Puerto')
                nuevo.save()
            ParqueSolar.objects.update()
            return response
        else:
            logger.debug(form.errors)
            contenido.toastrStatus = "error"
            contenido.toastrMsg = "Información no se ha guardado. Revise el formulario nuevamente."

    if form is None:
        form = ParqueFormFull(instance=parque)

    return TemplateResponse(request, 'vista/configuracion.html',
                            {'cont': contenido,
                                'parque': parque,
                                'form': form,
                                'aerogeneradores': aerogeneradores,
                             })


@login_required(login_url='ingresar')
@permission_required('vista.change_parquesolar', raise_exception=True)
def aerogeneradores(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo = u'Listado de Aerogeneradores'
    contenido.subtitulo = 'Parque ' + parque.nombre
    contenido.menu = ['menu-principal', 'menu2-aerogeneradores']
    observadores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    response_data = {}

    # Me decido por interfaz RESTful. POST: Crear Nuevo, DELETE: Eliminar, PUT: Editar
    if request.method == 'POST':
        logger.debug('POST Aerogeneradores')
        editar = Aerogenerador.objects.get(idx=int(request.POST['id']), parque=parque)
        editar.nombre = request.POST['nombre']
        try:
            editar.save()
            log_msg = "Se edita Aerogenerador - " + editar.nombre + " - idx=" + str(editar.idx)
            log = Log(texto=log_msg, tipo=2, user=request.user)
            log.save()
        except IntegrityError as e:
            logger.debug(e)
            return HttpResponse(status=409)
        response_data['id'] = str(editar.idx)
        response = json.dumps(response_data)
        return HttpResponse(
            response,
            content_type="application/json"
        )

    return TemplateResponse(request, 'vista/agregarAerogenerador.html',
                            {'cont': contenido,
                                'parque': parque,
                                'observadores': observadores,
                                'aerogeneradores':aerogeneradores,
                             })