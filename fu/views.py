# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from vista.models import ParqueSolar, Aerogenerador
from vista.functions import *
from fu.forms import ComponenteForm, AddComponentesForm, ConfiguracionFUForm,PlanificacionForm,DeleteComponentesForm
from fu.forms import RegistroDescargaForm, RegistroForm, ParadasForm
from fu.models import Componente, ComponentesParque, RelacionesFU, ConfiguracionFU, Contractual, Plan, EstadoFU
from fu.models import Registros, Paradas
from django.contrib import messages
from django.db.models import Max
from collections import OrderedDict
from django.http import HttpResponse, HttpResponseRedirect
from querystring_parser import parser
from dateutil import relativedelta
from datetime import datetime
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font, Color
from openpyxl import load_workbook
from django.core.urlresolvers import reverse
import StringIO
from django.conf import settings
import os
from ncr.views import serializeGrafico
from django.db.models import Sum
import numpy as np

meses_espanol={"1":"Enero",
       "2":"Febrero",
       "3":"Marzo",
       "4":"Abril",
       "5":"Mayo",
       "6":"Junio",
       "7":"Julio",
       "8":"Agosto",
       "9":"Septiembre",
       "10":"Octubre",
       "11":"Noviembre",
       "12":"Diciembre",
       }

import json
logger = logging.getLogger('oritec')

def graficoComponentes(componentes_parque,estado,anho,semana):
    data_full = []
    # Me entrega el domingo final de esa semana.
    d = str(anho) + '-W' + str(semana)
    r = datetime.strptime(d + '-0', "%Y-W%W-%w")
    max_aerogeneradores = componentes_parque.parque.no_aerogeneradores
    if estado.idx == 1:
        filtro = 'relacionesfu__orden_descarga'
    elif estado.idx == 3:
        filtro = 'relacionesfu__orden_montaje'
    karws = {filtro+'__gt': 0}
    componentes = componentes_parque.componentes.all()

    # Los totales
    data_graficos = []
    for s in componentes.filter(**karws).order_by(filtro):
        data_graficos.append({"name": s.nombre, "y": max_aerogeneradores})
    data_full.append({"name": "Total", "data": data_graficos})

    # Contractual
    data_graficos = []

    for s in componentes.filter(**karws).order_by(filtro):
        c = Contractual.objects.filter(parque=componentes_parque.parque,
                                       componente=s,
                                       estado=estado,
                                       fecha__lte=r).aggregate(Sum('no_aerogeneradores'))
        if c['no_aerogeneradores__sum'] is None:
            data_graficos.append({"name": s.nombre, "y": 0})
        else:
            data_graficos.append({"name": s.nombre, "y": c['no_aerogeneradores__sum']})
    data_full.append({"name": "Contractual", "data": data_graficos})

    # Plan
    data_graficos = []
    for s in componentes.filter(**karws).order_by(filtro):
        c = Plan.objects.filter(parque=componentes_parque.parque,
                                       componente=s,
                                       estado=estado,
                                       fecha__lte=r).aggregate(Sum('no_aerogeneradores'))
        if c['no_aerogeneradores__sum'] is None:
            data_graficos.append({"name": s.nombre, "y": 0})
        else:
            data_graficos.append({"name": s.nombre, "y": c['no_aerogeneradores__sum']})
    data_full.append({"name": "Plan", "data": data_graficos})
    # Real

    data_graficos = []
    for s in componentes.filter(**karws).order_by(filtro):
        c = Registros.objects.filter(parque=componentes_parque.parque,
                                componente=s,
                                estado=estado,
                                fecha__lte=r)
        data_graficos.append({"name": s.nombre, "y": c.count()})
    data_full.append({"name": "Real", "data": data_graficos})

    datos = serializeGrafico(data_full)
    return datos

def calcularProyeccion(componentes_parque,anho,semana):
    d = str(anho) + '-W' + str(semana)
    # Se calcula solo con los datos de hasta la semana pasada
    r = datetime.strptime(d + '-0', "%Y-W%W-%w") - relativedelta.relativedelta(weeks=1)
    parque = componentes_parque.parque
    try:
        configuracion = ConfiguracionFU.objects.get(parque=parque)
    except ConfiguracionFU.DoesNotExist:
        return [[], None]
    max_aerogeneradores = parque.no_aerogeneradores
    aux = RelacionesFU.objects.filter(componentes_parque=componentes_parque,
                                      orden_montaje__range=(1, 8))
    componentes_montaje = []
    for c in aux:
        componentes_montaje.append(c.componente.id)
    estado = EstadoFU.objects.get(idx=3)
    # Calculo
    fecha = configuracion.fecha_inicio
    semana_calculo = fecha.isocalendar()[1]
    d = str(fecha.year) + '-W' + str(semana_calculo)
    fecha_calculo = datetime.strptime(d + '-0', "%Y-W%W-%w")
    # Valores a numpy
    x_values = []
    y_values = []
    first = False
    first_date = None
    count = 0

    while fecha_calculo <= r:
        c = Registros.objects.filter(parque=parque,
                                     componente__in=componentes_montaje,
                                     estado=estado,
                                     fecha__lte=fecha_calculo)
        valor = float(c.count()) / 8
        if not first:
            if valor != 0:
                first = True
                first_date = fecha_calculo
        if first:
            if valor < max_aerogeneradores:
                x_values.append(count)
                y_values.append(valor)
                count += 1

        fecha = fecha_calculo + relativedelta.relativedelta(weeks=1)
        semana_calculo = fecha.isocalendar()[1]
        d = str(fecha.year) + '-W' + str(semana_calculo)
        fecha_calculo = datetime.strptime(d + '-0', "%Y-W%W-%w")

    if len(x_values) < 2:
        return [[], None]
    # Proyeccion
    x = np.array(x_values)
    y = np.array(y_values)
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    fecha = configuracion.fecha_inicio
    semana_calculo = fecha.isocalendar()[1]
    d = str(fecha.year) + '-W' + str(semana_calculo)
    fecha_calculo = datetime.strptime(d + '-0', "%Y-W%W-%w")
    data_graficos = []
    count = 0
    valor = 0
    while valor < max_aerogeneradores:
        if fecha_calculo < first_date:
            valor = 0
        else:
            valor = p(count)
            if valor < 0:
                valor = 0
            elif valor > max_aerogeneradores:
                valor = max_aerogeneradores
            count += 1
        fecha_grafico = str(fecha_calculo.year) + '-' + str(semana_calculo)
        valor_porcentaje = valor / max_aerogeneradores * 100
        data_graficos.append({"name": fecha_grafico, "y": valor_porcentaje})
        if valor < max_aerogeneradores:
            fecha = fecha_calculo + relativedelta.relativedelta(weeks=1)
            semana_calculo = fecha.isocalendar()[1]
            d = str(fecha.year) + '-W' + str(semana_calculo)
            fecha_calculo = datetime.strptime(d + '-0', "%Y-W%W-%w")
    return [data_graficos,fecha_calculo]

def aerogeneradoresMontados(componentes_parque,fecha):
    parque = componentes_parque.parque
    aux = RelacionesFU.objects.filter(componentes_parque=componentes_parque,
                                      orden_montaje=8)
    componente = aux[0].componente
    estado = EstadoFU.objects.get(idx=3)

    c = Registros.objects.filter(parque=parque,
                                 componente=componente,
                                 estado=estado,
                                 fecha__lte=fecha)
    return c.count()

def porcentajeAvance(componentes_parque,fecha,componentes_montaje=None):
    parque = componentes_parque.parque
    max_aerogeneradores = parque.no_aerogeneradores
    if componentes_montaje is None:
        aux = RelacionesFU.objects.filter(componentes_parque=componentes_parque,
                                          orden_montaje__range=(1, 8))
        componentes_montaje = []
        for c in aux:
            componentes_montaje.append(c.componente.id)
    estado = EstadoFU.objects.get(idx=3)

    c = Registros.objects.filter(parque=parque,
                                 componente__in=componentes_montaje,
                                 estado=estado,
                                 fecha__lte=fecha)
    valor = float(c.count()) / 8
    valor = valor / max_aerogeneradores * 100
    return valor

def graficoAvances(componentes_parque,anho,semana,anho2,semana2,data_proyeccion):
    data_full = []
    d = str(anho) + '-W' + str(semana)
    r = datetime.strptime(d + '-0', "%Y-W%W-%w")
    d = str(anho2) + '-W' + str(semana2)
    r2 = datetime.strptime(d + '-0', "%Y-W%W-%w")
    parque = componentes_parque.parque
    try:
        configuracion = ConfiguracionFU.objects.get(parque=parque)
    except ConfiguracionFU.DoesNotExist:
        return data_full
    max_aerogeneradores = parque.no_aerogeneradores
    aux = RelacionesFU.objects.filter(componentes_parque=componentes_parque,
                                                      orden_montaje__range=(1,8))
    componentes_montaje =[]
    for c in aux:
        componentes_montaje.append(c.componente.id)
    estado = EstadoFU.objects.get(idx=3)
    # Contractual
    fecha = configuracion.fecha_inicio
    semana_calculo = fecha.isocalendar()[1]
    d = str(fecha.year) + '-W' + str(semana_calculo)
    fecha_calculo = datetime.strptime(d + '-0', "%Y-W%W-%w")
    data_graficos = []
    while fecha_calculo <= r:
        c = Contractual.objects.filter(parque=parque,
                                   componente__in = componentes_montaje,
                                   estado = estado,
                                   fecha__lte= fecha_calculo).aggregate(Sum('no_aerogeneradores'))
        fecha_grafico = str(fecha_calculo.year) + '-' + str(semana_calculo)
        if c['no_aerogeneradores__sum'] is None:
            valor = 0
        else:
            valor = float(c['no_aerogeneradores__sum']) / 8 /max_aerogeneradores*100
        data_graficos.append({"name": fecha_grafico, "y": valor})
        fecha = fecha_calculo + relativedelta.relativedelta(weeks=1)
        semana_calculo = fecha.isocalendar()[1]
        d = str(fecha.year) + '-W' + str(semana_calculo)
        fecha_calculo = datetime.strptime(d + '-0', "%Y-W%W-%w")
    data_full.append({"name": "Contractual", "data": data_graficos})

    # Plan
    fecha = configuracion.fecha_inicio
    semana_calculo = fecha.isocalendar()[1]
    d = str(fecha.year) + '-W' + str(semana_calculo)
    fecha_calculo = datetime.strptime(d + '-0', "%Y-W%W-%w")
    data_graficos = []
    while fecha_calculo <= r:
        c = Plan.objects.filter(parque=parque,
                                       componente__in=componentes_montaje,
                                       estado=estado,
                                       fecha__lte=fecha_calculo).aggregate(Sum('no_aerogeneradores'))
        fecha_grafico = str(fecha_calculo.year) + '-' + str(semana_calculo)
        if c['no_aerogeneradores__sum'] is None:
            valor = 0
        else:
            valor = float(c['no_aerogeneradores__sum']) / 8 / max_aerogeneradores*100
        data_graficos.append({"name": fecha_grafico, "y": valor})
        fecha = fecha_calculo + relativedelta.relativedelta(weeks=1)
        semana_calculo = fecha.isocalendar()[1]
        d = str(fecha.year) + '-W' + str(semana_calculo)
        fecha_calculo = datetime.strptime(d + '-0', "%Y-W%W-%w")
    data_full.append({"name": "Plan", "data": data_graficos})

    # Real
    fecha = configuracion.fecha_inicio
    semana_calculo = fecha.isocalendar()[1]
    d = str(fecha.year) + '-W' + str(semana_calculo)
    fecha_calculo = datetime.strptime(d + '-0', "%Y-W%W-%w")
    data_graficos = []

    while fecha_calculo <= r2:
        valor = porcentajeAvance(componentes_parque,fecha_calculo,componentes_montaje=componentes_montaje)
        fecha_grafico = str(fecha_calculo.year) + '-' + str(semana_calculo)
        data_graficos.append({"name": fecha_grafico, "y": valor})
        fecha = fecha_calculo + relativedelta.relativedelta(weeks=1)
        semana_calculo = fecha.isocalendar()[1]
        d = str(fecha.year) + '-W' + str(semana_calculo)
        fecha_calculo = datetime.strptime(d + '-0', "%Y-W%W-%w")
    data_full.append({"name": "Real", "data": data_graficos})

    if len(data_proyeccion):
        data_full.append({"name": "Proyeccion", "data": data_proyeccion,"dashStyle" : "Dot"})


    datos = serializeGrafico(data_full)
    return datos

def posicionAerogeneradores(componentes_parque,anho,semana):
    parque = componentes_parque.parque
    d = str(anho) + '-W' + str(semana)
    fecha = datetime.strptime(d + '-0', "%Y-W%W-%w")
    estado = EstadoFU.objects.get(idx=3)
    pos = OrderedDict()
    for ag in Aerogenerador.objects.filter(parque=parque):
        pos[ag.nombre]={}

    pos['WTG01']['width'] = 7.0
    pos['WTG01']['top'] = 57.9
    pos['WTG01']['left'] = 6.9
    pos['WTG01']['zindex'] = 403

    pos['WTG02']['width'] = 7.0
    pos['WTG02']['top'] = 56.2
    pos['WTG02']['left'] = 12.9
    pos['WTG02']['zindex'] = 303

    pos['WTG03']['width'] = 7.0
    pos['WTG03']['top'] = 55
    pos['WTG03']['left'] = 18.5
    pos['WTG03']['zindex'] = 303

    pos['WTG04']['width'] = 7.0
    pos['WTG04']['top'] = 53.4
    pos['WTG04']['left'] = 24.0
    pos['WTG04']['zindex'] = 303

    pos['WTG05']['width'] = 7.0
    pos['WTG05']['top'] = 51.9
    pos['WTG05']['left'] = 29.5
    pos['WTG05']['zindex'] = 303

    pos['WTG06']['width'] = 7.0
    pos['WTG06']['top'] = 50.5
    pos['WTG06']['left'] = 34.9
    pos['WTG06']['zindex'] = 303

    pos['WTG07']['width'] = 7.0
    pos['WTG07']['top'] = 49.0
    pos['WTG07']['left'] = 40.1
    pos['WTG07']['zindex'] = 303

    pos['WTG08']['width'] = 7.0
    pos['WTG08']['top'] = 47.9
    pos['WTG08']['left'] = 45.5
    pos['WTG08']['zindex'] = 303
    #
    pos['WTG09']['width'] = 7.0
    pos['WTG09']['top'] = 46.5
    pos['WTG09']['left'] = 50.3
    pos['WTG09']['zindex'] = 303

    pos['WTG10']['width'] = 7.0
    pos['WTG10']['top'] = 45.4
    pos['WTG10']['left'] = 55.4
    pos['WTG10']['zindex'] = 303

    pos['WTG11']['width'] = 7.0
    pos['WTG11']['top'] = 44.3
    pos['WTG11']['left'] = 60.3
    pos['WTG11']['zindex'] = 303

    pos['WTG12']['width'] = 7.0
    pos['WTG12']['top'] = 43.0
    pos['WTG12']['left'] = 65.4
    pos['WTG12']['zindex'] = 303

    pos['WTG13']['width'] = 7.0
    pos['WTG13']['top'] = 41.8
    pos['WTG13']['left'] = 70.1
    pos['WTG13']['zindex'] = 303

    pos['WTG14']['width'] = 7.0
    pos['WTG14']['top'] = 40.6
    pos['WTG14']['left'] = 74.6
    pos['WTG14']['zindex'] = 303

    pos['WTG15']['width'] = 7.0
    pos['WTG15']['top'] = 38.9
    pos['WTG15']['left'] = 79.2
    pos['WTG15']['zindex'] = 303

    pos['WTG16']['width'] = 7.0
    pos['WTG16']['top'] = 38.0
    pos['WTG16']['left'] = 83.7
    pos['WTG16']['zindex'] = 303

    pos['WTG17']['width'] = 7.0
    pos['WTG17']['top'] = 36.6
    pos['WTG17']['left'] = 88.3
    pos['WTG17']['zindex'] = 303

    pos['WTG35']['width'] = 7.0
    pos['WTG35']['top'] = 30.6
    pos['WTG35']['left'] = 5.2
    pos['WTG35']['zindex'] = 103

    pos['WTG36']['width'] = 7.0
    pos['WTG36']['top'] = 29.5
    pos['WTG36']['left'] = 10.1
    pos['WTG36']['zindex'] = 103

    pos['WTG37']['width'] = 7.0
    pos['WTG37']['top'] = 28.5
    pos['WTG37']['left'] = 14.6
    pos['WTG37']['zindex'] = 103

    pos['WTG38']['width'] = 7.0
    pos['WTG38']['top'] = 27.4
    pos['WTG38']['left'] = 19.2
    pos['WTG38']['zindex'] = 103

    pos['WTG39']['width'] = 7.0
    pos['WTG39']['top'] = 26.3
    pos['WTG39']['left'] = 24.0
    pos['WTG39']['zindex'] = 103

    pos['WTG40']['width'] = 7.0
    pos['WTG40']['top'] = 25.5
    pos['WTG40']['left'] = 28.5
    pos['WTG40']['zindex'] = 103

    pos['WTG41']['width'] = 7.0
    pos['WTG41']['top'] = 24.8
    pos['WTG41']['left'] = 33.0
    pos['WTG41']['zindex'] = 103

    pos['WTG42']['width'] = 7.0
    pos['WTG42']['top'] = 23.5
    pos['WTG42']['left'] = 37.4
    pos['WTG42']['zindex'] = 103
    #

    pos['WTG43']['width'] = 7.0
    pos['WTG43']['top'] = 22.8
    pos['WTG43']['left'] = 41.7
    pos['WTG43']['zindex'] = 303

    pos['WTG44']['width'] = 7.0
    pos['WTG44']['top'] = 22.0
    pos['WTG44']['left'] = 45.9
    pos['WTG44']['zindex'] = 303

    pos['WTG45']['width'] = 7.0
    pos['WTG45']['top'] = 21.0
    pos['WTG45']['left'] = 50.1
    pos['WTG45']['zindex'] = 303

    pos['WTG46']['width'] = 7.0
    pos['WTG46']['top'] = 20.1
    pos['WTG46']['left'] = 54.3
    pos['WTG46']['zindex'] = 303

    pos['WTG47']['width'] = 7.0
    pos['WTG47']['top'] = 19.3
    pos['WTG47']['left'] = 58.5
    pos['WTG47']['zindex'] = 303

    pos['WTG48']['width'] = 7.0
    pos['WTG48']['top'] = 18.2
    pos['WTG48']['left'] = 62.3
    pos['WTG48']['zindex'] = 303

    pos['WTG49']['width'] = 7.0
    pos['WTG49']['top'] = 17.4
    pos['WTG49']['left'] = 66.3
    pos['WTG49']['zindex'] = 303

    pos['WTG50']['width'] = 7.0
    pos['WTG50']['top'] = 16.7
    pos['WTG50']['left'] = 70.0
    pos['WTG50']['zindex'] = 303

    pos['WTG51']['width'] = 7.0
    pos['WTG51']['top'] = 15.8
    pos['WTG51']['left'] = 74.0
    pos['WTG51']['zindex'] = 303

    pos['WTG60']['width'] = 7.0
    pos['WTG60']['top'] = 13.7
    pos['WTG60']['left'] = 38.4
    pos['WTG60']['zindex'] = 203

    pos['WTG61']['width'] = 7.0
    pos['WTG61']['top'] = 13.0
    pos['WTG61']['left'] = 42.4
    pos['WTG61']['zindex'] = 203

    pos['WTG62']['width'] = 7.0
    pos['WTG62']['top'] = 12.1
    pos['WTG62']['left'] = 46.2
    pos['WTG62']['zindex'] = 203

    pos['WTG63']['width'] = 7.0
    pos['WTG63']['top'] = 11.2
    pos['WTG63']['left'] = 50.0
    pos['WTG63']['zindex'] = 203

    pos['WTG69']['width'] = 7.0
    pos['WTG69']['top'] = 11
    pos['WTG69']['left'] = 3.9
    pos['WTG69']['zindex'] = 103

    pos['WTG70']['width'] = 7.0
    pos['WTG70']['top'] = 10.3
    pos['WTG70']['left'] = 7.9
    pos['WTG70']['zindex'] = 103

    pos['WTG71']['width'] = 7.0
    pos['WTG71']['top'] = 9.7
    pos['WTG71']['left'] = 11.9
    pos['WTG71']['zindex'] = 103

    pos['WTG72']['width'] = 7.0
    pos['WTG72']['top'] = 9.0
    pos['WTG72']['left'] = 16.0
    pos['WTG72']['zindex'] = 103

    pos['WTG73']['width'] = 7.0
    pos['WTG73']['top'] = 8.3
    pos['WTG73']['left'] = 20.0
    pos['WTG73']['zindex'] = 103

    pos['WTG74']['width'] = 7.0
    pos['WTG74']['top'] = 7.5
    pos['WTG74']['left'] = 24.0
    pos['WTG74']['zindex'] = 103

    pos['WTG75']['width'] = 7.0
    pos['WTG75']['top'] = 6.8
    pos['WTG75']['left'] = 27.8
    pos['WTG75']['zindex'] = 103

    pos['WTG76']['width'] = 7.0
    pos['WTG76']['top'] = 6.1
    pos['WTG76']['left'] = 31.6
    pos['WTG76']['zindex'] = 103

    pos['WTG77']['width'] = 7.0
    pos['WTG77']['top'] = 5.3
    pos['WTG77']['left'] = 35.2
    pos['WTG77']['zindex'] = 103

    pos['WTG78']['width'] = 7.0
    pos['WTG78']['top'] = 5
    pos['WTG78']['left'] = 38.9
    pos['WTG78']['zindex'] = 103

    pos['WTG79']['width'] = 7.0
    pos['WTG79']['top'] = 4.3
    pos['WTG79']['left'] = 42.9
    pos['WTG79']['zindex'] = 103

    pos['WTG80']['width'] = 7.0
    pos['WTG80']['top'] = 3.7
    pos['WTG80']['left'] = 46.3
    pos['WTG80']['zindex'] = 103

    pos['WTG81']['width'] = 7.0
    pos['WTG81']['top'] = 3.0
    pos['WTG81']['left'] = 50.0
    pos['WTG81']['zindex'] = 103

    pos['WTG82']['width'] = 7.0
    pos['WTG82']['top'] = 2.3
    pos['WTG82']['left'] = 53.3
    pos['WTG82']['zindex'] = 103

    pos['WTG83']['width'] = 7.0
    pos['WTG83']['top'] = 1.8
    pos['WTG83']['left'] = 56.8
    pos['WTG83']['zindex'] = 103

    pos['WTG84']['width'] = 7.0
    pos['WTG84']['top'] = 1.2
    pos['WTG84']['left'] = 60.2
    pos['WTG84']['zindex'] = 103

    pos['WTG85']['width'] = 7.0
    pos['WTG85']['top'] = 0.6
    pos['WTG85']['left'] = 63.7
    pos['WTG85']['zindex'] = 103


    for ag in Aerogenerador.objects.filter(parque=parque,idx__gte=0):
        if ag.nombre in pos:
            pos[ag.nombre]['url'] = reverse('fu:ingreso', args=(parque.slug,ag.slug))
        registros = Registros.objects.filter(parque=parque,
                                             aerogenerador=ag,
                                             estado=estado,
                                             fecha__lte=fecha)
        if registros.count() > 0:
            reg_ids = []
            for r in registros:
                reg_ids.append(r.componente.id)
            rel = RelacionesFU.objects.filter(componentes_parque=componentes_parque,
                                              componente__in=reg_ids).order_by('-orden_montaje')
            if rel.count() > 0:
                orden = rel[0].orden_montaje
                if orden >= 8:
                    imagen = str(8)
                    pos[ag.nombre]['width'] = 4.5
                    pos[ag.nombre]['top'] = pos[ag.nombre]['top'] + 5.4
                    pos[ag.nombre]['left'] = pos[ag.nombre]['left'] +1.4
                elif orden == 1:
                    imagen = str(orden)
                    pos[ag.nombre]['width'] = 0.5
                    pos[ag.nombre]['top'] = pos[ag.nombre]['top'] + 12.7
                    pos[ag.nombre]['left'] = pos[ag.nombre]['left'] + 3.7
                elif orden == 2:
                    imagen = str(orden)
                    pos[ag.nombre]['width'] = 0.6
                    pos[ag.nombre]['top'] = pos[ag.nombre]['top'] + 11.1
                    pos[ag.nombre]['left'] = pos[ag.nombre]['left'] + 3.7
                elif orden == 3:
                    imagen = str(orden)
                    pos[ag.nombre]['width'] = 0.5
                    pos[ag.nombre]['top'] = pos[ag.nombre]['top'] + 10.1
                    pos[ag.nombre]['left'] = pos[ag.nombre]['left'] +3.7
                elif orden == 4:
                    imagen = str(orden)
                    pos[ag.nombre]['width'] = 0.65
                    pos[ag.nombre]['top'] = pos[ag.nombre]['top'] + 8.8
                    pos[ag.nombre]['left'] = pos[ag.nombre]['left'] +3.6
                elif orden == 5:
                    imagen = str(orden)
                    pos[ag.nombre]['width'] = 0.8
                    pos[ag.nombre]['top'] = pos[ag.nombre]['top'] + 8.7
                    pos[ag.nombre]['left'] = pos[ag.nombre]['left'] +3.7
                elif orden == 6:
                    imagen = str(orden)
                    pos[ag.nombre]['width'] = 1.1
                    pos[ag.nombre]['top'] = pos[ag.nombre]['top'] + 5.8
                    pos[ag.nombre]['left'] = pos[ag.nombre]['left'] +3.4
                elif orden == 7:
                    imagen = str(orden)
                    pos[ag.nombre]['width'] = 4.2
                    pos[ag.nombre]['top'] = pos[ag.nombre]['top'] + 8.4
                    pos[ag.nombre]['left'] = pos[ag.nombre]['left'] +1.4
                else:
                    imagen = str(orden)
                pos[ag.nombre]['img'] = 'common/images/ag/' + imagen + '.png'
            else:
                pos[ag.nombre]['width'] = 0.5
                pos[ag.nombre]['top'] = pos[ag.nombre]['top'] + 12.7
                pos[ag.nombre]['left'] = pos[ag.nombre]['left'] + 3.7
                pos[ag.nombre]['img'] = 'common/images/ag/0.png'
        else:
            pos[ag.nombre]['width'] = 0.5
            try:
                pos[ag.nombre]['top'] = pos[ag.nombre]['top'] + 12.7
            except:
                pass;
            pos[ag.nombre]['left'] = pos[ag.nombre]['left'] + 3.7
            pos[ag.nombre]['img'] = 'common/images/ag/0.png'

    return pos

@login_required(login_url='ingresar')
def dashboard(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    try:
        componentes_parque = ComponentesParque.objects.get(parque=parque)
    except ComponentesParque.DoesNotExist:
        componentes_parque = ComponentesParque(parque=parque)
        componentes_parque.save()

    contenido = ContenidoContainer()
    contenido.user = request.user
    contenido.titulo = u'Dashboard Follow Up'
    contenido.subtitulo = u'Parque Eólico - ' + parque.nombre
    contenido.menu = ['menu-fu', 'menu2-dashboard']

    try:
        configuracion = ConfiguracionFU.objects.get(parque=parque)
    except ConfiguracionFU.DoesNotExist:
        return render(request, 'fu/dashboard.html',
                      {'cont': contenido,
                       'parque': parque,
                       'aerogeneradores': aerogeneradores,
                       'configuracion': None,
                       })

    t = datetime.now()
    anho = t.year
    semana = t.isocalendar()[1]
    semana_today = t.isocalendar()[1]
    if request.method == 'POST':
        if 'semana' in request.POST:
            values = request.POST['semana'].split('-')
            anho = int(values[0])
            semana = int(values[1])
    d = str(anho) + '-W' + str(semana)
    last_day_week = datetime.strptime(d + '-0', "%Y-W%W-%w")

    estado = EstadoFU.objects.get(idx=1)
    graficoDescarga = graficoComponentes(componentes_parque,estado,anho,semana)
    estado = EstadoFU.objects.get(idx=3)
    graficoMontaje = graficoComponentes(componentes_parque, estado, anho, semana)
    [proyeccion, last_week] = calcularProyeccion(componentes_parque, anho, semana)
    if last_week is not None:
        graficoAvance = graficoAvances(componentes_parque, last_week.year, last_week.isocalendar()[1], anho,semana,proyeccion)
    else:
        fecha_aux = configuracion.fecha_final
        semana_calculo = fecha_aux.isocalendar()[1]
        d = str(fecha_aux.year) + '-W' + str(semana_calculo)
        fecha_calculo = datetime.strptime(d + '-0', "%Y-W%W-%w")
        graficoAvance = graficoAvances(componentes_parque, fecha_calculo.year, fecha_calculo.isocalendar()[1], anho, semana,
                                       proyeccion)

    thisweek = str(anho) + "-" + str(semana)
    week_str = 'Semana ' + str(semana)
    if semana == semana_today:
        fecha = t
    else:
        d = str(anho) + '-W' + str(semana)
        fecha = datetime.strptime(d + '-0', "%Y-W%W-%w")
    pos_ag = posicionAerogeneradores(componentes_parque,anho,semana)

    fecha_aux= configuracion.fecha_inicio #+ relativedelta.relativedelta(weeks=1)
    semana_calculo = fecha_aux.isocalendar()[1]
    d = str(fecha_aux.year) + '-W' + str(semana_calculo)
    fecha_inicial = datetime.strptime(d + '-0', "%Y-W%W-%w")

    avance = porcentajeAvance(componentes_parque,last_day_week)
    montados = aerogeneradoresMontados(componentes_parque,last_day_week)
    try:
        componente = Componente.objects.get(nombre="Mechanical Completion")
        estado = EstadoFU.objects.get(idx=3)
        c = Registros.objects.filter(parque=parque,
                                     componente=componente,
                                     estado=estado,
                                     fecha__lte=last_day_week)
        mechanical = c.count()
    except Componente.DoesNotExist:
        mechanical = 0

    try:
        componente = Componente.objects.get(nombre="Commisioning")
        estado = EstadoFU.objects.get(idx=4)
        c = Registros.objects.filter(parque=parque,
                                     componente=componente,
                                     estado=estado,
                                     fecha__lte=last_day_week)
        ag_ready = c.count()
    except Componente.DoesNotExist:
        ag_ready = 0


    return render(request, 'fu/dashboard.html',
                  {'cont': contenido,
                   'parque': parque,
                   'aerogeneradores': aerogeneradores,
                   'graficoDescarga': graficoDescarga,
                   'graficoMontaje': graficoMontaje,
                   'graficoAvance': graficoAvance,
                   'thisweek': thisweek,
                   'week_str': week_str,
                   'fecha': fecha,
                   'pos_ag': pos_ag,
                   'configuracion': configuracion,
                   'fecha_inicial' : fecha_inicial,
                   'avance':avance,
                   'montados':montados,
                   'mechanical': mechanical,
                   'ag_ready': ag_ready,
                   })

@login_required(login_url='ingresar')
def avance(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    try:
        componentes_parque = ComponentesParque.objects.get(parque=parque)
    except ComponentesParque.DoesNotExist:
        componentes_parque = ComponentesParque(parque=parque)
        componentes_parque.save()

    contenido = ContenidoContainer()
    contenido.user = request.user
    contenido.titulo = u'Avance'
    contenido.subtitulo = u'Parque Eólico - ' + parque.nombre
    contenido.menu = ['menu-fu', 'menu2-avance']

    pos_ag = posicionAerogeneradores(componentes_parque,2017,39)

    return render(request, 'fu/avance.html',
                  {'cont': contenido,
                   'parque': parque,
                   'aerogeneradores': aerogeneradores,
                   'pos_ag': pos_ag,
                   })

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
            c = get_object_or_404(Componente, id=int(request.POST['del_id']))
            c.delete()
            messages.add_message(request, messages.SUCCESS, 'Componente eliminado.')
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
    ret_d = 0
    ret_p = 0
    ret_m = 0
    ret_pm = 0
    for e in componente.estados.all():
        if e.idx == 1:
            ret_d = d + 1
        elif e.idx == 2:
            ret_p = p + 1
        elif e.idx == 3:
            ret_m = m + 1
        elif e.idx == 4:
            ret_pm = pm + 1
    return [ret_d,ret_p,ret_m,ret_pm]

def getComponentesbyState(componentes_parque, estado):
    if estado == 'descarga':
        orden = 'orden_descarga'
        indice = 1
    elif estado == 'premontaje':
        orden = 'orden_premontaje'
        indice = 2
    elif estado == 'montaje':
        orden = 'orden_montaje'
        indice = 3
    elif estado == 'puestaenmarcha':
        orden = 'orden_puestaenmarcha'
        indice = 4
    else:
        return None

    lista = OrderedDict()
    componentes = componentes_parque.componentes.all()
    filtro = 'relacionesfu__' + orden
    karws = {filtro + '__gt': 0}
    id = 0
    for c in componentes.filter(**karws).order_by(filtro):
        lista[c.id]=c.nombre
        id += 1
    return lista

def addComponente(componentes_parque, new_componente):
    aux = RelacionesFU.objects.filter(componentes_parque=componentes_parque)
    if aux.exists():
        maximos = aux.aggregate(Max('orden_descarga'),
                                Max('orden_premontaje'),
                                Max('orden_montaje'),
                                Max('orden_puestaenmarcha'))
        descarga = maximos['orden_descarga__max']
        premontaje = maximos['orden_premontaje__max']
        montaje = maximos['orden_montaje__max']
        puestaenmarcha = maximos['orden_puestaenmarcha__max']
    else:
        descarga = 0
        premontaje = 0
        montaje = 0
        puestaenmarcha = 0
    [descarga, premontaje, montaje, puestaenmarcha] = getOrden(new_componente,
                                                               descarga,
                                                               premontaje,
                                                               montaje,
                                                               puestaenmarcha)

    r = RelacionesFU(componentes_parque=componentes_parque,
                     componente=new_componente,
                     orden_descarga=descarga,
                     orden_premontaje=premontaje,
                     orden_montaje=montaje,
                     orden_puestaenmarcha=puestaenmarcha)
    r.save()

def deleteComponente(componentes_parque, del_componente):
    aux = RelacionesFU.objects.get(componentes_parque=componentes_parque, componente=del_componente)
    if aux.orden_descarga > 0:
        aux2=RelacionesFU.objects.filter(componentes_parque=componentes_parque, orden_descarga__gt = aux.orden_descarga)
        for c in aux2:
            c.orden_descarga += -1
            c.save()
    if aux.orden_premontaje > 0:
        aux2=RelacionesFU.objects.filter(componentes_parque=componentes_parque, orden_premontaje__gt = aux.orden_premontaje)
        for c in aux2:
            c.orden_premontaje += -1
            c.save()
    if aux.orden_montaje > 0:
        aux2=RelacionesFU.objects.filter(componentes_parque=componentes_parque, orden_montaje__gt = aux.orden_montaje)
        for c in aux2:
            c.orden_montaje += -1
            c.save()
    if aux.orden_puestaenmarcha > 0:
        aux2=RelacionesFU.objects.filter(componentes_parque=componentes_parque, orden_puestaenmarcha__gt = aux.orden_puestaenmarcha)
        for c in aux2:
            c.orden_puestaenmarcha += -1
            c.save()
    aux.delete()

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
        if 'delComponente' in request.POST:
            deleteComponentesForm = DeleteComponentesForm(request.POST, parque=parque)
            if deleteComponentesForm.is_valid():
                deleteComponente(componentes_parque,deleteComponentesForm.cleaned_data['componente'])
        elif 'addComponente' in request.POST:
            choicesComponentesForm = AddComponentesForm(request.POST, parque=parque)
            if choicesComponentesForm.is_valid():
                addComponente(componentes_parque,choicesComponentesForm.cleaned_data['componente'])

    choicesComponentesForm = AddComponentesForm(parque = parque)
    deleteComponentesForm = DeleteComponentesForm(parque = parque)
    lista_descarga = getComponentesbyState(componentes_parque,'descarga')
    lista_premontaje = getComponentesbyState(componentes_parque,'premontaje')
    lista_montaje = getComponentesbyState(componentes_parque,'montaje')
    lista_puestaenmarcha = getComponentesbyState(componentes_parque,'puestaenmarcha')

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
         'deleteComponentesForm': deleteComponentesForm,
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
            obj = RelacionesFU.objects.get(componente__id=id)
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

def checkValidFile(ws, componentes_parque):
    fila = 4
    columna = 2
    valor = ws.cell(row=fila,column=columna).value
    while valor is not None:
        elementos = componentes_parque.componentes.filter(nombre=valor)
        if elementos.count() <= 0:
            logger.debug('Archivo inválido')
            return -1
        fila = fila +2
        valor = ws.cell(row=fila, column=columna).value

    return fila

def getLastColumn(ws):
    fila = 3
    columna = 4
    valor = ws.cell(row=fila,column=columna).value
    while valor is not None:
        # Verifica que los nombres sean componentes válidos
        columna = columna + 2
        valor = ws.cell(row=fila, column=columna).value
    return columna

@login_required(login_url='ingresar')
def configuracion(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    try:
        configuracion = ConfiguracionFU.objects.get(parque=parque)
    except ConfiguracionFU.DoesNotExist:
        configuracion = None

    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Parque Eólico'
    contenido.subtitulo= parque.nombre
    contenido.menu = ['menu-fu', 'menu2-configuracionfu']

    form = None

    if request.method == 'POST':
        if configuracion is None:
            form = ConfiguracionFUForm(request.POST)
        else:
            form = ConfiguracionFUForm(request.POST, instance=configuracion)
        if form.is_valid():
            if configuracion is None:
                conf = form.save(commit=False)
                conf.parque = parque
                conf.save()
            else:
                form.save()
            messages.add_message(request, messages.SUCCESS, 'Configuración guardada con éxito')
        else:
            messages.add_message(request, messages.ERROR, 'Configuración no se ha podido guardar.')

    if form is None:
        if configuracion is None:
            form = ConfiguracionFUForm()
        else:
            form = ConfiguracionFUForm(instance=configuracion)
    return render(request, 'fu/configuracion.html',
                  {'cont': contenido,
                   'parque': parque,
                   'aerogeneradores': aerogeneradores,
                   'form': form
                   })

def readPlanFile(configuracion, componentes_parque):
    nombre_archivo = os.path.join(settings.MEDIA_ROOT, configuracion.plan.name)
    wb = load_workbook(nombre_archivo)
    ws = wb.active
    last_row = checkValidFile(ws, componentes_parque)
    if last_row == -1:
        # Retorna falso, no se pudo leer este archivo correctamente.
        return False
    else:
        # si está bien el archivo, entonces hay que borrar la planificación para el parque antes de insertar la nueva.
        objs = Plan.objects.filter(parque = configuracion.parque)
        for obj in objs:
            obj.delete()
        objs = Contractual.objects.filter(parque = configuracion.parque)
        for obj in objs:
            obj.delete()
    last_column = getLastColumn(ws)
    fila = 4
    ultimo_estado = None
    ultimo_anho = None
    estado = None
    while fila < last_row:
        columna = 4
        nombre_componente = ws.cell(row=fila, column=2).value
        # lo puedo hacer de forma segura, porque se supone que los validé en checkValidFile
        componente = Componente.objects.get(nombre=nombre_componente)
        nombre_estado = ws.cell(row=fila, column=1).value

        if nombre_estado is not None:
            if nombre_estado != ultimo_estado:
                ultimo_estado = nombre_estado
                estado = None
                if ultimo_estado == 'Descarga en Parque':
                    estado = EstadoFU.objects.get(idx=1)
                elif ultimo_estado == 'Pre-montaje':
                    estado = EstadoFU.objects.get(idx=2)
                elif ultimo_estado == 'Montaje':
                    estado = EstadoFU.objects.get(idx=3)
                elif ultimo_estado == 'Puesta en marcha':
                    estado = EstadoFU.objects.get(idx=4)
                else:
                    estado = None
                    logger.debug('No existe el estado')

        if ultimo_estado is not None and estado is not None:
            while columna < last_column:
                semana = ws.cell(row=3, column=columna).value
                anho = ws.cell(row=1, column=columna).value
                if anho is not None:
                    if anho != ultimo_anho:
                        ultimo_anho = anho
                contractual = ws.cell(row=fila,column = columna).value
                plan = ws.cell(row=fila+1,column = columna).value
                d = ultimo_anho + "-W" + semana + "-0"
                fecha = datetime.strptime(d, "%Y-W%W-%w")
                if plan is not None:
                    plan = int(plan)
                    if plan != 0:
                        nuevo = Plan(parque = configuracion.parque,
                                     componente = componente,
                                     estado = estado,
                                     fecha = fecha,
                                     no_aerogeneradores=plan)
                        nuevo.save()

                if contractual is not None:
                    contractual = int(contractual)
                    if contractual != 0:
                        nuevo = Contractual(parque = configuracion.parque,
                                     componente = componente,
                                     estado= estado,
                                     fecha = fecha,
                                     no_aerogeneradores=contractual)
                        nuevo.save()

                columna += 1
        fila += 2
    return True

def graficoPlanificacion(parque):
    configuracion = ConfiguracionFU.objects.get(parque=parque)
    componentes_parque = ComponentesParque.objects.get(parque=parque)
    aux = configuracion.fecha_inicio
    final = configuracion.fecha_final
    xvalues = {}
    yvalues = {}
    plan_values = {}
    contractual_values = {}
    for i in range(1,5):
        xlabels = '['
        ylabels = '['
        plan = '['
        contractual = '['
        idx = 0
        idy = 0
        first = True
        aux = configuracion.fecha_inicio
        while aux < final:
            semana = str(aux.isocalendar()[1])
            anho = aux.year
            d = str(anho) + "-W" + semana + "-0"
            fecha_query = datetime.strptime(d, "%Y-W%W-%w")
            xlabels += '"'+ str(anho) + '-' + semana + '",'
            idy = 0
            for componente in componentes_parque.componentes.all():
                e = None
                for aux_e in componente.estados.all():
                    if aux_e.idx == i:
                        e = aux_e
                        break
                if e is not None:
                    if first:
                        ylabels += '"' + componente.nombre + '",'
                    try:
                        q = Plan.objects.get(parque=parque, componente=componente, estado=e,fecha=fecha_query)
                        val = q.no_aerogeneradores
                    except Plan.DoesNotExist:
                        val = 0
                    plan += '['+str(idx)+','+str(idy)+','+str(val)+'],'
                    try:
                        q = Contractual.objects.get(parque=parque, componente=componente, estado=e,fecha=fecha_query)
                        val = q.no_aerogeneradores
                    except Contractual.DoesNotExist:
                        val = 0
                    contractual += '['+str(idx)+','+str(idy)+','+str(val)+'],'
                    idy += 1
            first = False
            idx += 1
            aux = aux + relativedelta.relativedelta(weeks=1)
        xlabels = xlabels[:-1] + ']'
        ylabels = ylabels[:-1] + ']'
        plan = plan[:-1] + ']'
        contractual = contractual[:-1] + ']'
        xvalues[i] = xlabels
        yvalues[i] = ylabels
        plan_values[i] = plan
        contractual_values[i] = contractual
    return [xvalues,yvalues,plan_values,contractual_values]

@login_required(login_url='ingresar')
def planificacion(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    try:
        componentes_parque = ComponentesParque.objects.get(parque=parque)
    except ComponentesParque.DoesNotExist:
        componentes_parque = ComponentesParque(parque=parque)
        componentes_parque.save()

    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo= u'Planificación Follow Up'
    contenido.subtitulo= u'Parque Eólico ' +parque.nombre
    contenido.menu = ['menu-fu', 'menu2-planificacion']

    try:
        configuracion = ConfiguracionFU.objects.get(parque=parque)
    except ConfiguracionFU.DoesNotExist:
        configuracion = None


    form = None

    if request.method == 'POST':
        form = PlanificacionForm(request.POST, request.FILES, instance=configuracion)
        if form.is_valid():
            configuracion = form.save()

        if configuracion.plan:
            if configuracion.plan != configuracion.prev_plan:
                readPlanFile(configuracion,componentes_parque)
            else:
                logger.debug('Se sube configuración, pero se mantiene igual.')

    if form is None and configuracion is not None:
        form = PlanificacionForm(instance = configuracion)

    if configuracion:
        [x_axis, y_axis, plan,contractual] = graficoPlanificacion(parque)
    else:
        x_axis = None
        y_axis = None
        plan = None
        contractual = None

    aux = datetime.today()
    semana = str(aux.isocalendar()[1])
    anho = aux.year
    thisweek = str(anho) + "-" + semana

    return render(request, 'fu/planificacion.html',
                  {'cont': contenido,
                   'parque': parque,
                   'aerogeneradores': aerogeneradores,
                   'configuracion': configuracion,
                   'form': form,
                   'x_axis': x_axis,
                   'y_axis': y_axis,
                   'plan': plan,
                   'contractual': contractual,
                   'thisweek': thisweek
                   })

@login_required(login_url='ingresar')
def download_config(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    try:
        configuracion = ConfiguracionFU.objects.get(parque=parque)
    except ConfiguracionFU.DoesNotExist:
        return

    try:
        componentes_parque = ComponentesParque.objects.get(parque=parque)
    except ComponentesParque.DoesNotExist:
        componentes_parque = ComponentesParque(parque=parque)
        componentes_parque.save()

    aux = configuracion.fecha_inicio
    final = configuracion.fecha_final

    semanas = []
    meses = {}
    anhos = {}
    semana = str(aux.isocalendar()[1])
    semanas.append(semana)
    meses[semana] = meses_espanol[str(aux.month)]
    anhos[semana] = str(aux.year)
    aux = aux + relativedelta.relativedelta(weeks=1)
    while aux < final:
        semana = str(aux.isocalendar()[1])
        semanas.append(semana)
        meses[semana] = meses_espanol[str(aux.month)]
        anhos[semana] = str(aux.year)
        aux = aux + relativedelta.relativedelta(weeks=1)

    wb = Workbook()
    ws = wb.active
    ws.title = "Planificacion"
    bgColor = Color(rgb="283861")
    bg = PatternFill(patternType='solid', fgColor=bgColor)
    font = Font(color="FFFFFF")
    thin = Side(border_style="thin", color="000000")
    solid = Side(border_style="medium", color="000000")
    borderfull = Border(top=thin, left=thin, right=thin, bottom=thin)
    bordertop = Border(top=thin, left=thin, right=thin)
    borderbottom = Border(left=thin, right=thin, bottom=thin)
    borderside = Border(left=thin, right=thin)
    # alignment = Alignment(horizontal="center", vertical="center",text_rotation =90, wrap_text = False, shrink_to_fit = False, indent = 0)
    alignment1 = Alignment(horizontal="center", vertical="center", text_rotation=90)
    alignment2 = Alignment(vertical="center")
    alignment3 = Alignment(horizontal="center")
    alignment4 = Alignment(horizontal="center", wrap_text = True)

    row = 3
    column = 4
    idx = 0

    d = ws.cell(row=row, column=1, value='Actividad')
    d.fill = bg
    d.font = font
    d.border = borderfull
    d.alignment = alignment3
    d = ws.cell(row=row, column=2, value='Componente')
    d.fill = bg
    d.font = font
    d.border = borderfull
    d.alignment = alignment3
    d = ws.cell(row=row, column=3, value='Semana')
    d.fill = bg
    d.font = font
    d.border = borderfull
    d.alignment = alignment3

    ws.column_dimensions["A"].width = 11.0
    ws.column_dimensions["B"].width = 25.0
    ws.column_dimensions["C"].width = 11.0
    prev_year = ''
    prev_month = ''
    prev_month_col = 0
    prev_year_col = 0

    for s in semanas:
        d = ws.cell(row=row, column=column+idx, value=semanas[idx])
        d.fill = bg
        d.font = font
        d.border = borderfull
        d.alignment = alignment3
        if prev_year != anhos[semanas[idx]]:
            prev_year = anhos[semanas[idx]]
            d = ws.cell(row=row-2, column=column + idx, value=prev_year)
            d.fill = bg
            d.font = font
            d.alignment = alignment4
            if prev_year_col == 0:
                prev_year_col = column + idx
            else:
                ws.merge_cells(start_row=row-2, start_column=prev_year_col, end_row=row - 2, end_column=column+ idx -1)
                prev_year_col = column + idx

        if prev_month != meses[semanas[idx]]:
            prev_month = meses[semanas[idx]]
            d = ws.cell(row=row-1, column=column + idx, value=prev_month)
            d.fill = bg
            d.font = font
            d.border = borderfull
            d.alignment = alignment4
            if prev_month_col == 0:
                prev_month_col = column + idx
            else:
                ws.merge_cells(start_row=row-1, start_column=prev_month_col, end_row=row - 1, end_column=column+ idx -1)
                prev_month_col = column + idx
        idx += 1
    ws.merge_cells(start_row=row - 2, start_column=prev_year_col, end_row=row - 2, end_column=column + idx - 1)
    ws.merge_cells(start_row=row - 1, start_column=prev_month_col, end_row=row - 1, end_column=column + idx - 1)

    for aux_col in range(4,column+idx):
        d = ws.cell(row=row - 2, column=aux_col)
        d.border = borderbottom

    estados = OrderedDict()
    estados['descarga'] = 'Descarga en Parque'
    estados['premontaje'] = 'Pre-montaje'
    estados['montaje'] = 'Montaje'
    estados['puestaenmarcha'] = 'Puesta en marcha'
    #estados = ['descarga','premontaje','montaje','puestaenmarcha']
    estados_db = {}
    estados_db['descarga'] = EstadoFU.objects.get(idx=1)
    estados_db['premontaje'] = EstadoFU.objects.get(idx=2)
    estados_db['montaje'] = EstadoFU.objects.get(idx=3)
    estados_db['puestaenmarcha'] = EstadoFU.objects.get(idx=4)

    column = 2
    row = 4

    planExist = False
    if Plan.objects.filter(parque=parque).count()>0:
        planExist = True
    if Contractual.objects.filter(parque=parque).count()>0:
        planExist = True

    for e, titulo in estados.iteritems():
        componentes = getComponentesbyState(componentes_parque,e)
        if len(componentes) > 0:
            d = ws.cell(row=row, column=1, value=titulo)
            d.alignment = alignment1
            d.fill = bg
            d.font = font
            d.border = borderfull
            first_row = row
            first = True
            for idx, nombre in componentes.iteritems():
                d=ws.cell(row=row, column=column , value=nombre)
                d.alignment = alignment2
                d.fill = bg
                d.font = font
                ws.merge_cells(start_row=row, start_column=column, end_row=row + 1, end_column=column)
                if first:
                    d.border = bordertop
                    d = ws.cell(row=row + 1, column=column)
                    d.border = borderside
                    first = False
                else:
                    d.border = borderside
                    d = ws.cell(row=row+1, column=column)
                    d.border = borderside

                d2 = ws.cell(row=row, column=column+1, value='Contractual')
                d2.border = bordertop
                d2.alignment = alignment3
                d2 = ws.cell(row=row+1, column=column + 1, value='Plan')
                d2.border = borderbottom
                d2.alignment = alignment3
                columna_aux = 4
                if planExist :
                    for semana in semanas:
                        d_str = anhos[semana] + "-W" + semana + "-0"
                        fecha_aux = datetime.strptime(d_str, "%Y-W%W-%w")
                        try:
                            plan = Plan.objects.get(parque=parque,
                                                    componente__nombre=nombre,
                                                    estado=estados_db[e],
                                                    fecha=fecha_aux)
                            ws.cell(row=row+1, column=columna_aux, value=plan.no_aerogeneradores)
                        except Plan.DoesNotExist:
                            pass
                        try:
                            contractual = Contractual.objects.get(parque=parque,
                                                                  componente__nombre=nombre,
                                                                  estado=estados_db[e],
                                                                  fecha=fecha_aux)
                            ws.cell(row=row , column=columna_aux, value=contractual.no_aerogeneradores)
                        except Contractual.DoesNotExist:
                            pass
                        columna_aux += 1

                row += 2
            d.border = borderbottom
            ws.merge_cells(start_row=first_row, start_column=1, end_row=row-1, end_column=1)


    target_stream = StringIO.StringIO()
    wb.save(target_stream)
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="PlantilaPlanificacion.xlsx"'
    target_stream.flush()
    ret_excel = target_stream.getvalue()
    target_stream.close()
    response.write(ret_excel)
    return response

# 2: El componente-estado ya fue ingresado
# 1: El componente-estado está bloqueado por prerequisitos
# 0: El componente-estado puede ser ingresado
def getComponenteStatus(registros,idx,componente,relaciones):
    aux = registros.filter(componente=componente, estado__idx=idx)
    if aux.count() > 0:
        return 2

    if idx == 1: # Estado descarga
        return 0
    elif idx == 3: # Estado montaje
        if componente.estados.all().filter(idx__lt=3).count() > 0:
            aux2 = registros.filter(componente=componente, estado__idx=1) # Si está abierto el componente en descarga
            if aux2.count()>0:
                c_aux = relaciones.get(componente=componente)
                c_ids = []
                for c in relaciones.filter(orden_montaje__lt=c_aux.orden_montaje, orden_montaje__gt=0):
                    c_ids.append(c.componente.id)
                aux3 = registros.filter(componente_id__in=c_ids,estado__idx=3)
                if aux3.count() == len(c_ids):
                    return 0
                else:
                    return 1
            else:
                return 1
        else:
            c_aux = relaciones.get(componente=componente)
            c_ids = []
            for c in relaciones.filter(orden_montaje__lt=c_aux.orden_montaje, orden_montaje__gt=0):
                c_ids.append(c.componente.id)
            aux3 = registros.filter(componente_id__in=c_ids, estado__idx=3)
            if aux3.count() == len(c_ids):
                return 0
            else:
                return 1
    elif idx == 4: # Estado puesta en marcha
        c_ids = []
        for c in relaciones.filter(orden_montaje__gt=0):
            c_ids.append(c.componente.id)
        aux3 = registros.filter(componente_id__in=c_ids, estado__idx=3)
        if aux3.count() == len(c_ids):
            return 0
        else:
            return 1
    else:
        return 1

    return 1

@login_required(login_url='ingresar')
def ingreso(request,slug,slug_ag):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    aerogenerador = get_object_or_404(Aerogenerador, parque=parque, slug=slug_ag)
    try:
        configuracion = ConfiguracionFU.objects.get(parque=parque)
    except ConfiguracionFU.DoesNotExist:
        configuracion = None

    try:
        componentes_parque = ComponentesParque.objects.get(parque=parque)
    except ComponentesParque.DoesNotExist:
        componentes_parque = ComponentesParque(parque=parque)
        componentes_parque.save()

    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo= u'Ingreso Registros Aerogenerador ' + aerogenerador.nombre
    contenido.subtitulo= u'Parque Eólico ' +parque.nombre
    contenido.menu = ['menu-fu', 'menu2-ingreso-'+str(aerogenerador.idx)]

    if request.method == 'POST':
        registro = None
        if 'formDescarga' in request.POST:
            formDescarga= RegistroDescargaForm(request.POST)
            if formDescarga.is_valid():
                registro = formDescarga.save(commit=False)
                estado = EstadoFU.objects.get(idx=1)
            else:
                messages.add_message(request, messages.ERROR, 'Registro no pudo realizarse')
        elif 'formMontaje' in request.POST:
            form = RegistroForm(request.POST)
            if form.is_valid():
                registro = form.save(commit=False)
                estado = EstadoFU.objects.get(idx=3)
            else:
                messages.add_message(request, messages.ERROR, 'Registro no pudo realizarse')
        elif 'formPuestaenmarcha' in request.POST:
            form = RegistroForm(request.POST)
            if form.is_valid():
                registro = form.save(commit=False)
                estado = EstadoFU.objects.get(idx=4)
            else:
                messages.add_message(request, messages.ERROR, 'Registro no pudo realizarse')
        elif 'delete' in request.POST:
            componente_id = int(request.POST['del_id'])
            estado_id = int(request.POST['del_estado_id'])
            c = Componente.objects.get(id=componente_id)
            reg = Registros.objects.get(parque=parque, aerogenerador=aerogenerador,componente=c, estado__idx=estado_id)
            reg.delete()
            messages.add_message(request, messages.SUCCESS, 'Registro eliminado con éxito!')
        if registro is not None:
            registro.parque = parque
            registro.aerogenerador = aerogenerador
            componente_id = int(request.POST['id'])
            componente = Componente.objects.get(id=componente_id)
            registro.componente = componente
            registro.estado = estado
            registro.save()
            messages.add_message(request, messages.SUCCESS, 'Registro realizado con éxito!')

    componentes = OrderedDict()

    componentes['Descarga en Parque'] = {}
    componentes['Montaje'] = {}
    componentes['Puesta en marcha'] = {}

    registros = Registros.objects.filter(parque=parque, aerogenerador=aerogenerador)
    relaciones = RelacionesFU.objects.filter(componentes_parque = componentes_parque)

    componentes['Descarga en Parque']['objetos'] = []
    for c in componentes_parque.componentes.all().filter(estados__idx=1):
        aux = getComponenteStatus(registros, 1, c, relaciones)
        objeto = {}
        color = 'bg-yellow-crusta'
        if aux == 2:
            color = 'bg-green-meadow'
            reg = registros.get(componente=c,estado__idx=1)
            objeto['tooltip'] = reg.fecha.strftime("%d/%m/%Y") + '<br>' + reg.no_serie
        objeto['componente'] = c
        objeto['color'] = color
        objeto['status'] = aux
        objeto['estado'] = 1
        componentes['Descarga en Parque']['objetos'].append(objeto)

    componentes['Montaje']['objetos']  = []
    for c in componentes_parque.componentes.all().filter(estados__idx=3):
        aux = getComponenteStatus(registros, 3, c, relaciones)
        color = 'bg-grey-salt'
        objeto = {}
        if aux == 2:
            color = 'bg-green-meadow'
            reg = registros.get(componente=c, estado__idx=3)
            objeto['tooltip'] = reg.fecha.strftime("%d/%m/%Y")
        elif aux == 0:
            color = 'bg-yellow-crusta'
        objeto['componente'] = c
        objeto['color'] = color
        objeto['status'] = aux
        objeto['estado'] = 3
        componentes['Montaje']['objetos'].append(objeto)


    componentes['Puesta en marcha']['objetos']  = []
    filtro = 'relacionesfu__orden_puestaenmarcha'
    karws = {filtro + '__gt': 0}

    for c in componentes_parque.componentes.all().filter(**karws).order_by(filtro):
        aux = getComponenteStatus(registros, 4, c, relaciones)
        color = 'bg-grey-salt'
        objeto = {}
        if aux == 2:
            color = 'bg-green-meadow'
            reg = registros.get(componente=c, estado__idx=4)
            objeto['tooltip'] = reg.fecha.strftime("%d/%m/%Y")
        elif aux == 0:
            color = 'bg-yellow-crusta'
        objeto['componente'] = c
        objeto['color'] = color
        objeto['status'] = aux
        objeto['estado'] = 4
        componentes['Puesta en marcha']['objetos'].append(objeto)


    componentes['Descarga en Parque']['id'] = 'descarga'
    componentes['Montaje']['id'] = 'montaje'
    componentes['Puesta en marcha']['id'] = 'puestaenmarcha'

    componentes['Descarga en Parque']['icon'] = 'fa-map-marker'
    componentes['Montaje']['icon'] = 'fa-cogs'
    componentes['Puesta en marcha']['icon'] = 'fa-thumbs-o-up'


    formDescarga = RegistroDescargaForm()
    form = RegistroForm()

    pos = {}
    estado = EstadoFU.objects.get(idx=3)
    registros_aux = Registros.objects.filter(parque=parque,
                                         aerogenerador=aerogenerador,
                                         estado=estado)
    if registros_aux.count() > 0:
        reg_ids = []
        for r in registros_aux:
            reg_ids.append(r.componente.id)
        rel = RelacionesFU.objects.filter(componentes_parque=componentes_parque,
                                          componente__in=reg_ids).order_by('-orden_montaje')
        if rel.count() > 0:
            orden = rel[0].orden_montaje
            if orden >= 8:
                imagen = str(8)
                pos['width'] = 75
                pos['top'] =  10
                pos['left'] = 4 # OK
            elif orden == 1:
                imagen = str(orden)
                pos['width'] = 7
                pos['top'] =  136
                pos['left'] = 43 #OK
            elif orden == 2:
                imagen = str(orden)
                pos['width'] = 10
                pos['top'] = 110
                pos['left'] = 42 #OK
            elif orden == 3:
                imagen = str(orden)
                pos['width'] = 11
                pos['top'] = 64
                pos['left'] = 41 #OK
            elif orden == 4:
                imagen = str(orden)
                pos['width'] = 11
                pos['top'] = 63
                pos['left'] = 42 #OK
            elif orden == 5:
                imagen = str(orden)
                pos['width'] = 14
                pos['top'] =  60
                pos['left'] = 38 #OK
            elif orden == 6:
                imagen = str(orden)
                pos['width'] = 20
                pos['top'] = 3
                pos['left'] = 36 # OK
            elif orden == 7:
                imagen = str(orden)
                pos['width'] = 73
                pos['top'] = 55
                pos['left'] = 2
            pos['img'] = 'common/images/ag/' + imagen + '.png'
    return render(request, 'fu/ingreso.html',
                  {'cont': contenido,
                   'parque': parque,
                   'aerogeneradores': aerogeneradores,
                   'form': form,
                   'componentes': componentes,
                   'aerogenerador': aerogenerador,
                   'formDescarga': formDescarga,
                   'registros':registros.order_by('fecha'),
                   'pos':pos,
                   })

@login_required(login_url='ingresar')
def paradas(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Listado de Paradas '
    contenido.subtitulo='Parque '+ parque.nombre
    contenido.menu = ['menu-fu', 'menu2-paradas']

    paradas = Paradas.objects.all()

    if request.method == 'POST':
        if 'del_id' in request.POST:
            id = int(request.POST['del_id'])
            parada = Paradas.objects.get(id=id)
            parada.delete()
            messages.add_message(request, messages.SUCCESS, 'Registro eliminado con éxito!')
        else:
            messages.add_message(request, messages.ERROR, 'Error al eliminar registro')

    return render(request, 'fu/paradas.html',
        {'cont': contenido,
            'parque': parque,
            'aerogeneradores': aerogeneradores,
            'paradas': paradas,
        })

@login_required(login_url='ingresar')
def add_paradas(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Listado de Paradas '
    contenido.subtitulo='Parque '+ parque.nombre
    contenido.menu = ['menu-fu', 'menu2-paradas']

    form = None

    if request.method == 'POST':
        form = ParadasForm(request.POST,initial={'parque':parque})
        if form.is_valid():
            parada = form.save(commit=False)
            parada.parque = parque
            parada.save()
            messages.add_message(request, messages.SUCCESS, 'Registro agregado con éxito!')
            return HttpResponseRedirect(reverse('fu:paradas', args=[parque.slug]))
        else:
            messages.add_message(request, messages.ERROR, 'Error al agregar el registro')


    if form is None:
        form = ParadasForm(initial={'parque':parque})
    back_url = reverse('fu:paradas', args=[parque.slug])
    return render(request, 'fu/agregarParada.html',
        {'cont': contenido,
            'parque': parque,
            'form': form,
            'back_url':back_url,
            'aerogeneradores': aerogeneradores,
        })

@login_required(login_url='ingresar')
def edit_paradas(request,slug,id):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    parada = get_object_or_404(Paradas, id=id)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Listado de Paradas '
    contenido.subtitulo='Parque '+ parque.nombre
    contenido.menu = ['menu-fu', 'menu2-paradas']

    form = None

    if request.method == 'POST':
        form = ParadasForm(request.POST, instance=parada)
        if form.is_valid():
            parada = form.save()
            messages.add_message(request, messages.SUCCESS, 'Registro editado con éxito!')
            return HttpResponseRedirect(reverse('fu:paradas', args=[parque.slug]))
        else:
            messages.add_message(request, messages.SUCCESS, 'Error al editar el registro')

    if form is None:
        form = ParadasForm(instance=parada)
    back_url = reverse('fu:paradas', args=[parque.slug])
    edit_parada = parada
    return render(request, 'fu/agregarParada.html',
        {'cont': contenido,
            'parque': parque,
            'form': form,
            'aerogeneradores': aerogeneradores,
            'back_url':back_url,
            'edit_parada': edit_parada,
        })