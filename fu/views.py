# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from vista.models import ParqueSolar, Aerogenerador
from vista.functions import *
from fu.forms import ComponenteForm, ActividadesComponentesForm
from fu.models import Componente, ComponentesParque, RelacionesFU
from django.contrib import messages
from django.db.models import Max
from collections import OrderedDict
from django.http import HttpResponse
import json
logger = logging.getLogger('oritec')
from querystring_parser import parser

# Create your views here.
@login_required(login_url='ingresar')
def componente(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Componentes Follow Up'
    contenido.subtitulo=u'Parque Eólico - ' + parque.nombre
    contenido.menu = ['menu-fu', 'menu2-componentes']

    if request.method == 'POST':
        if 'delete' in request.POST:
            logger.debug('Componente a eliminar id=' + request.POST['del_id'])
        elif 'id' in request.POST:
            logger.debug('Componente a editar id=' + request.POST['id'])
            c = get_object_or_404(Componente, id=int(request.POST['id']))
            inputForm = ComponenteForm(request.POST)
            if inputForm.is_valid():
                c.nombre = inputForm.cleaned_data['nombre']
                c.estados.clear()
                for e in inputForm.cleaned_data['estadofu']:
                    c.estados.add(e)
                c.save()
        else:
            inputForm = ComponenteForm(request.POST)
            if inputForm.is_valid():
                logger.debug('Formulario válido')
                c = Componente(nombre=inputForm.cleaned_data['nombre'])
                c.save()
                for e in inputForm.cleaned_data['estadofu']:
                    c.estados.add(e)
                c.save()
                messages.add_message(request, messages.SUCCESS, 'Componente Creado con éxito!')
            else:
                messages.add_message(request, messages.ERROR, 'Componente no pudo ser creado.')

    componenteForm = ComponenteForm()
    componentes = Componente.objects.all().order_by('id')
    return render(request, 'fu/componentes.html',
        {'cont': contenido,
         'parque': parque,
         'aerogeneradores':aerogeneradores,
         'componenteForm': componenteForm,
         'componentes': componentes,
        })

def getOrden(componente, d,p,m,pm):
    for e in componente.estados.all():
        if e.idx == 1:
            d += 1
        elif e.idx == 2:
            p += 1
        elif e.idx == 3:
            m += 1
        elif e.idx == 4:
            pm += 1
    return [d,p,m,pm]

@login_required(login_url='ingresar')
def actividades(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    try:
        componentes_parque = ComponentesParque.objects.get(parque=parque)
    except ComponentesParque.DoesNotExist:
        componentes_parque = ComponentesParque(parque=parque)
        componentes_parque.save()

    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Actividades Follow Up'
    contenido.subtitulo=u'Parque Eólico - ' + parque.nombre
    contenido.menu = ['menu-fu', 'menu2-actividades']

    if request.method == 'POST':
        choicesComponentesForm = ActividadesComponentesForm(request.POST, parque=parque)
        if choicesComponentesForm.is_valid():
            aux = RelacionesFU.objects.filter(componentes_parque=componentes_parque)
            if aux.exists():
                maximos = aux.aggregate(Max('orden_descarga'),
                                        Max('orden_premontaje'),
                                        Max('orden_montaje'),
                                        Max('orden_puestaenmarcha'))
                componente = choicesComponentesForm.cleaned_data['componente']
                descarga = maximos['orden_descarga__max']
                premontaje = maximos['orden_premontaje__max']
                montaje = maximos['orden_montaje__max']
                puestaenmarcha = maximos['orden_puestaenmarcha__max']
            else:
                componente = choicesComponentesForm.cleaned_data['componente']
                descarga = 0
                premontaje = 0
                montaje = 0
                puestaenmarcha = 0
            [descarga,premontaje,montaje,puestaenmarcha] = getOrden(componente,
                                                                    descarga,
                                                                    premontaje,
                                                                    montaje,
                                                                    puestaenmarcha)

            r = RelacionesFU(componentes_parque=componentes_parque,
                         componente= componente,
                         orden_descarga=descarga,
                         orden_premontaje=premontaje,
                         orden_montaje=montaje,
                         orden_puestaenmarcha=puestaenmarcha)
            r.save()

    choicesComponentesForm = ActividadesComponentesForm(parque = parque)
    lista_descarga = OrderedDict()
    lista_premontaje = OrderedDict()
    lista_montaje = OrderedDict()
    lista_puestaenmarcha = OrderedDict()

    for c in RelacionesFU.objects.filter(componentes_parque=componentes_parque).order_by('orden_descarga'):
        for e in c.componente.estados.all():
            if e.idx == 1:
                lista_descarga[c.id]=c.componente.nombre
    for c in RelacionesFU.objects.filter(componentes_parque=componentes_parque).order_by('orden_premontaje'):
        for e in c.componente.estados.all():
            if e.idx == 2:
                lista_premontaje[c.id] = c.componente.nombre
    for c in RelacionesFU.objects.filter(componentes_parque=componentes_parque).order_by('orden_montaje'):
        for e in c.componente.estados.all():
            if e.idx == 3:
                lista_montaje[c.id] = c.componente.nombre
    for c in RelacionesFU.objects.filter(componentes_parque=componentes_parque).order_by('orden_puestaenmarcha'):
        for e in c.componente.estados.all():
            if e.idx == 4:
                lista_puestaenmarcha[c.id] = c.componente.nombre
    estados = ['descarga','premontaje','montaje','puestaenmarcha']
    actividades = OrderedDict()
    actividades['descarga']=lista_descarga
    actividades['premontaje']= lista_premontaje
    actividades['montaje']= lista_montaje
    actividades['puestaenmarcha']= lista_puestaenmarcha

    titulos = {
        'descarga': 'Descarga',
        'premontaje': 'Pre-montaje',
        'montaje': 'Montaje',
        'puestaenmarcha': 'Puesta en marcha'
    }

    return render(request, 'fu/actividades.html',
        {'cont': contenido,
         'parque': parque,
         'aerogeneradores':aerogeneradores,
         'choicesComponentesForm': choicesComponentesForm,
         'actividades': actividades,
         'titulos': titulos,
        })

def ordenar_actividades(request, slug, estado):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    logger.debug("Ordenar Actividades, estado = " + estado)
    response_data = {}
    response_data['files'] = []
    if request.method == 'POST':
        response = json.dumps([])
        post_dict = parser.parse(request.POST.urlencode())
        datos = post_dict['lista']
        for pos, val in datos.iteritems():
            idx = pos +1
            id = int(val['id'])
            obj = RelacionesFU.objects.get(id=id)
            if estado == 'descarga':
                obj.orden_descarga = idx
            elif estado == 'premontaje':
                obj.orden_premontaje = idx
            elif estado == 'montaje':
                obj.orden_montaje = idx
            elif estado == 'puestaenmarcha':
                obj.orden_puestaenmarcha = idx
            obj.save()
        return HttpResponse(
            response,
            content_type="application/json"
        )