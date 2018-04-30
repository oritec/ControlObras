# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.template.response import TemplateResponse

from django.contrib.auth.decorators import login_required
from vista.functions import *
from django.shortcuts import get_object_or_404
from vista.models import ParqueSolar, Aerogenerador
from usuarios.models import Log
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from dr.forms import DRForm
from dr.models import DR, ActividadDR

import logging
logger = logging.getLogger('oritec')

@login_required(login_url='ingresar')
def listado(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    contenido = ContenidoContainer()
    contenido.user = request.user
    contenido.titulo = u'Informes diarios'
    contenido.subtitulo = parque.nombre
    contenido.menu = ['menu-dr', 'menu2-listado' ]


    return TemplateResponse(request, 'dr/listado.html',
                            {'cont': contenido,
                             'parque': parque,
                             'aerogeneradores': aerogeneradores
                             })

@login_required(login_url='ingresar')
def agregar(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    contenido = ContenidoContainer()
    contenido.user = request.user
    contenido.titulo = u'Informes diarios'
    contenido.subtitulo = parque.nombre
    contenido.menu = ['menu-dr', 'menu2-listado']

    form = None

    if request.method == 'POST':
        form = DRForm(request.POST)
        if form.is_valid():
            logger.debug('Formulario válido.')
            dr = form.save(commit=False)
            dr.created_by = request.user
            dr.save()
            log_msg = "Se agrega reporte diario para parque " + parque.nombre
            log = Log(texto=log_msg, tipo=1, user=request.user)
            log.save()
            dr.save() # Necesario para actualizar campos
            return HttpResponseRedirect(reverse('dr:dr-editar', args=[parque.slug,dr.id]))
        else:
            logger.debug('Formulario no es válido...')

    if form is None:
        form = DRForm(initial={'parque':parque.id})

    return TemplateResponse(request, 'dr/agregar.html',
                            {'cont': contenido,
                             'parque': parque,
                             'aerogeneradores': aerogeneradores,
                             'form': form,
                             })


@login_required(login_url='ingresar')
def editar(request,slug, dr_id):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    dr = get_object_or_404(DR, id=dr_id)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    contenido = ContenidoContainer()
    contenido.user = request.user
    contenido.titulo = u'Informes diarios'
    contenido.subtitulo = parque.nombre
    contenido.menu = ['menu-dr', 'menu2-listado']

    form = None

    if request.method == 'POST':
        form = DRForm(request.POST)
        if form.is_valid():
            logger.debug('Formulario válido.')
            dr = form.save(commit=False)
            dr.created_by = request.user
            dr.save()
            log_msg = "Se agrega reporte diario para parque " + parque.nombre
            log = Log(texto=log_msg, tipo=1, user=request.user)
            log.save()
            dr.save() # Necesario para actualizar campos
            #return HttpResponseRedirect(reverse('dr:observaciones-show', args=[parque.slug,observacion.id]))
        else:
            logger.debug('Formulario no es válido...')

    if form is None:
        form = DRForm(instance=dr)

    return TemplateResponse(request, 'dr/agregar.html',
                            {'cont': contenido,
                             'parque': parque,
                             'aerogeneradores': aerogeneradores,
                             'form': form,
                             'editar': True
                             })
