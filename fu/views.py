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
    # Los totales
    data_graficos = []
    for s in componentes_parque.componentes.all():
        if s.estados.all().filter(idx=estado.idx).count() > 0:
            data_graficos.append({"name": s.nombre, "y": 55})
    data_full.append({"name": "Total", "data": data_graficos})

    # Contractual
    data_graficos = []
    for s in componentes_parque.componentes.all():
        if s.estados.all().filter(idx=estado.idx).count() > 0:
            c = Contractual.objects.filter(parque=componentes_parque.parque,
                                           componente=s,
                                           estado=estado,
                                           fecha__lte=r).aggregate(Sum('no_aerogeneradores'))
            data_graficos.append({"name": s.nombre, "y": c['no_aerogeneradores__sum']})
    data_full.append({"name": "Contractual", "data": data_graficos})

    # Plan
    data_graficos = []
    for s in componentes_parque.componentes.all():
        if s.estados.all().filter(idx=estado.idx).count() > 0:
            c = Plan.objects.filter(parque=componentes_parque.parque,
                                           componente=s,
                                           estado=estado,
                                           fecha__lte=r).aggregate(Sum('no_aerogeneradores'))
            data_graficos.append({"name": s.nombre, "y": c['no_aerogeneradores__sum']})
    data_full.append({"name": "Plan", "data": data_graficos})
    # Real

    data_graficos = []
    for s in componentes_parque.componentes.all():
        if s.estados.all().filter(idx=estado.idx).count() > 0:
            c = Registros.objects.filter(parque=componentes_parque.parque,
                                    componente=s,
                                    estado=estado,
                                    fecha__lte=r)
            data_graficos.append({"name": s.nombre, "y": c.count()})
    data_full.append({"name": "Real", "data": data_graficos})


    datos = serializeGrafico(data_full)
    return datos

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

    estado = EstadoFU.objects.get(idx=1)
    graficoDescarga = graficoComponentes(componentes_parque,estado,2017,38)
    estado = EstadoFU.objects.get(idx=3)
    graficoMontaje = graficoComponentes(componentes_parque, estado, 2017, 38)

    return render(request, 'fu/dashboard.html',
                  {'cont': contenido,
                   'parque': parque,
                   'aerogeneradores': aerogeneradores,
                   'graficoDescarga': graficoDescarga,
                   'graficoMontaje': graficoMontaje,
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
    for c in RelacionesFU.objects.filter(componentes_parque=componentes_parque).order_by(orden):
        for e in c.componente.estados.all():
            if e.idx == indice:
                lista[c.id]=c.componente.nombre
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
    contenido.titulo= u'Planificación Follow Up'
    contenido.subtitulo= u'Parque Eólico ' +parque.nombre
    contenido.menu = ['menu-fu', 'menu2-planificacion']

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

    [x_axis, y_axis, plan,contractual] = graficoPlanificacion(parque)


    aux = datetime.today()
    semana = str(aux.isocalendar()[1])
    anho = aux.year
    thisweek = str(anho) + "-" + semana


    return render(request, 'fu/planificacion.html',
                  {'cont': contenido,
                   'parque': parque,
                   'aerogeneradores': aerogeneradores,
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

    column = 2
    row = 4

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
            c_ids.append(c.id)
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
    for c in componentes_parque.componentes.all().filter(estados__idx=4):
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

    return render(request, 'fu/ingreso.html',
                  {'cont': contenido,
                   'parque': parque,
                   'aerogeneradores': aerogeneradores,
                   'form': form,
                   'componentes': componentes,
                   'aerogenerador': aerogenerador,
                   'formDescarga': formDescarga,
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