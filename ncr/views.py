# -*- coding: utf-8 -*-
from django.shortcuts import render
from vista.functions import *
from django.contrib.auth.decorators import login_required
from vista.models import ParqueSolar,Aerogenerador
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from forms import ObservacionForm, RevisionForm, RevisionFormFull, NCR, Punchlist
from ncr.models import Observacion, Revision, Fotos, Observador,Componente,Subcomponente,Tipo,Severidad,EstadoRevision
from easy_pdf.rendering import render_to_pdf_response, render_to_pdf
from vista.models import Aerogenerador
import json
import logging
import os
import urlparse
import StringIO
import zipfile
import base64
from docx import Document
from docx.shared import Mm, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.shape import WD_INLINE_SHAPE
from django.conf import settings
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from datetime import date
from datetime import datetime
from django.core.serializers import serialize

logger = logging.getLogger('oritec')

@login_required(login_url='ingresar')
def home(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
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

def serializeGrafico(d):
    s = '['
    if len(d) > 0:
        for v in d:
            s += '{'
            for key, value in v.iteritems():
                if isinstance(value, (int, long, float, complex)):
                    s += key + ':'+ str(value) + ','
                elif isinstance(value,(dict,list)):
                    s2 = serializeGrafico(value)
                    s += key + ':' + s2 + ','
                else:
                    s +=  key + ':"' + value + '",'
            s = s[:-1]
            s += '},'
        s = s[:-1]

    s += ']'

    return s


def graficoBarrasSimple(resultados,field,secciones, showall = False):
    data_graficos = []
    count = 0
    for s in secciones:
        karws = {field: s}
        aux=resultados.filter(**karws)
        if (aux.count()>0 or showall):
            data_graficos.append({"name":s.graphText(),"y":aux.count()})
            count += 1

    datos= serializeGrafico(data_graficos)
    return datos


def graficoBarrasCompleto(resultados, field, secciones, showall = False):
    data_full = []
    count = 0
    filtros = Severidad.objects.all()
    for f in filtros:
        data_graficos = []
        karws = {'severidad': f}
        resultados_filtrados = resultados.filter(**karws)
        for s in secciones:
            karws = {field: s}
            aux=resultados_filtrados.filter(**karws)
            if (aux.count()>0 or showall):
                data_graficos.append({"name":s.graphText(),"y":aux.count()})
                count += 1
        data_full.append({"name": f.graphText(), "data": data_graficos})
    datos = serializeGrafico(data_full)
    return datos

@login_required(login_url='ingresar')
def observaciones_resumen(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Resumen de Observaciones'
    contenido.subtitulo='Parque '+parque.nombre
    contenido.menu = ['menu-ncr', 'menu2-observaciones-resumen']
    observaciones = Observacion.objects.filter(parque=parque)
    url_append = ''
    table_show_ag = True

    grafico_estado = graficoBarrasSimple(observaciones,'estado',EstadoRevision.objects.all().order_by('-id'),showall=True)
    grafico_severidad = graficoBarrasSimple(observaciones,'severidad',Severidad.objects.all(), showall=True)
    grafico_componente = graficoBarrasSimple(observaciones,'componente',Componente.objects.all())
    grafico_subcomponente = graficoBarrasSimple(observaciones, 'sub_componente', Subcomponente.objects.all())
    grafico_tipo = graficoBarrasSimple(observaciones, 'tipo', Tipo.objects.all())

    grafico_aerogenerador = graficoBarrasCompleto(observaciones,'aerogenerador',aerogeneradores, showall=True)

    return render(request, 'ncr/resumen.html',
                  {'cont': contenido,
                   'parque': parque,
                   'observaciones': observaciones,
                   'url_append':url_append,
                   'table_show_ag': table_show_ag,
                   'aerogeneradores':aerogeneradores,
                   'grafico_estado':grafico_estado,
                   'grafico_severidad': grafico_severidad,
                   'grafico_componente': grafico_componente,
                   'grafico_subcomponente': grafico_subcomponente,
                   'grafico_tipo': grafico_tipo,
                   'grafico_aerogenerador': grafico_aerogenerador,
                   })

@login_required(login_url='ingresar')
def observaciones(request,slug,slug_ag):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    aerogenerador = get_object_or_404(Aerogenerador,parque=parque,slug=slug_ag)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'NCR Aerogenerador '+ aerogenerador.nombre
    contenido.subtitulo='Parque '+ parque.nombre
    contenido.menu = ['menu-ncr', 'menu2-observaciones-'+str(aerogenerador.idx)]
    url_append='?aerogenerador='+str(aerogenerador.idx)

    observaciones = Observacion.objects.filter(aerogenerador__idx__exact=aerogenerador.idx, parque= parque)
    grafico_estado = graficoBarrasSimple(observaciones, 'estado', EstadoRevision.objects.all().order_by('-id'),
                                         showall=True)
    grafico_severidad = graficoBarrasSimple(observaciones, 'severidad', Severidad.objects.all(), showall=True)
    grafico_componente = graficoBarrasSimple(observaciones, 'componente', Componente.objects.all())
    grafico_subcomponente = graficoBarrasSimple(observaciones, 'sub_componente', Subcomponente.objects.all())
    grafico_tipo = graficoBarrasSimple(observaciones, 'tipo', Tipo.objects.all())

    return render(request, 'ncr/resumen.html',
        {'cont': contenido,
            'parque': parque,
            'observaciones': observaciones,
            'url_append': url_append,
            'aerogeneradores':aerogeneradores,
            'grafico_estado':grafico_estado,
            'grafico_severidad': grafico_severidad,
            'grafico_componente': grafico_componente,
            'grafico_subcomponente': grafico_subcomponente,
            'grafico_tipo': grafico_tipo,
        })

@login_required(login_url='ingresar')
def add_observacion(request,slug,observacion_id=0):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    edit_observacion = None
    if observacion_id != 0:
        edit_observacion = get_object_or_404(Observacion,id=observacion_id)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.subtitulo=parque.nombre
    if 'aerogenerador' in request.GET:
        contenido.titulo = u'Agregar Observación'
        contenido.menu = ['menu-ncr', 'menu2-observaciones-'+str(request.GET['aerogenerador'])]
        ag_readonly = True
        back_url = reverse('ncr:observaciones', args=[parque.slug,request.GET['aerogenerador']])
    elif edit_observacion is not None:
        contenido.titulo = u'Editar Observación'
        contenido.menu = ['menu-ncr', 'menu2-observaciones-' + str(edit_observacion.aerogenerador.idx)]
        ag_readonly = False
        back_url = reverse('ncr:observaciones-show', args=[parque.slug, str(edit_observacion.id)])
    else:
        contenido.titulo = u'Agregar Observación'
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
                # es necesario para actualizar el estado de la observacion
                observacion.save()
            else:
                observacion = observacionForm.save(commit=False)
                observacion.created_by = request.user
                observacion.save()
                revision = revisionForm.save(commit=False)
                revision.observacion = observacion
                revision.created_by = request.user
                revision.reported_by = observacion.reported_by
                revision.save()
                # es necesario para actualizar el estado de la observacion
                observacion.save()
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
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Observación OBS_' + parque.codigo +\
                     '-' + observacion.aerogenerador.nombre + '-' + str(observacion.observacion_id)
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

    template_name = 'ncr/showObservacion.html'

    if 'printable' in request.GET:
        template_name = 'ncr/showObservacion-printable.html'

    return render(request, template_name,
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
            if foto.principal:
                data={'name': os.path.basename(foto.imagen.name),
                      'size':str(foto.imagen.size),
                      'url':foto.imagen.url,
                      'thumbnailUrl':foto.thumbnail.url,
                      'deleteUrl':reverse('ncr:imagenes-delete',args=[parque.slug,foto.id]),
                      "deleteType": "DELETE",
                      "mainPhoto": foto.principal,
                      "photoId" : str(foto.id)}
                response_data['files'].append(data)
        for foto in results:
            if not foto.principal:
                data={'name': os.path.basename(foto.imagen.name),
                      'size':str(foto.imagen.size),
                      'url':foto.imagen.url,
                      'thumbnailUrl':foto.thumbnail.url,
                      'deleteUrl':reverse('ncr:imagenes-delete',args=[parque.slug,foto.id]),
                      "deleteType": "DELETE",
                      "mainPhoto": foto.principal,
                      "photoId" : str(foto.id)}
                response_data['files'].append(data)
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
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
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

def generateExcelNCR(resultados):
    wb = Workbook()
    ws = wb.active
    ws.title = "ReporteNCR"
    # Titulos
    ws['A1'] = 'WTG'
    ws['B1'] = 'Estado'
    ws['C1'] = 'Severidad'
    ws['D1'] = 'Componente'
    ws['E1'] = 'Subcomponente'
    ws['F1'] = 'Tipo'
    ws['G1'] = 'Descripcion'
    row = 1
    for r in resultados:
        row += 1
        ws.cell(row=row, column=1,value=r.aerogenerador.nombre)
        ws.cell(row=row, column=2, value=r.estado.nombre)
        ws.cell(row=row, column=3, value=r.severidad.nombre)
        ws.cell(row=row, column=4, value=r.componente.nombre)
        ws.cell(row=row, column=5, value=r.sub_componente.nombre)
        ws.cell(row=row, column=6, value=r.tipo.nombre)
        ws.cell(row=row, column=7, value=r.nombre)

    tab = Table(displayName="NCR", ref="A1:G"+str(row))
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    tab.tableStyleInfo = style
    ws.add_table(tab)
    dims = {}
    for row in ws.rows:
        for cell in row:
            if cell.value:
                dims[cell.column] = max((dims.get(cell.column, 0), len(cell.value)+4))
    for col, value in dims.items():
        ws.column_dimensions[col].width = value
    target_stream = StringIO.StringIO()
    wb.save(target_stream)
    return target_stream

@login_required(login_url='ingresar')
def informeNCR(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Informe NCRs'
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
            resultados = resultados.filter(severidad__in=form.cleaned_data['severidad'])
            resultados = resultados.filter(componente__in=form.cleaned_data['componente'])
            resultados = resultados.filter(sub_componente__in=form.cleaned_data['subcomponente'])
            resultados = resultados.filter(tipo__in=form.cleaned_data['tipo'])
            if (len(form.cleaned_data['condicion']) == 1):
                if 'reparadas' in form.cleaned_data['condicion']:
                    condicion = True
                else:
                    condicion = False
                resultados = resultados.filter(cerrado = condicion)
            elif (len(form.cleaned_data['condicion']) == 0):
                resultados = []

            if (len(form.cleaned_data['clase']) == 1):
                if '1' in form.cleaned_data['clase']:
                    clase = True
                else:
                    clase = False
                resultados = resultados.filter(clase = clase)
            elif (len(form.cleaned_data['clase']) == 0):
                resultados = []

            if (len(form.cleaned_data['punchlist']) == 1):
                if '1' in form.cleaned_data['punchlist']:
                    punchlist = True
                else:
                    punchlist = False
                resultados = resultados.filter(punchlist = punchlist)
            elif (len(form.cleaned_data['punchlist']) == 0):
                resultados = []
            #for key,value in form.cleaned_data.iteritems():
            #    logger.debug(key)
            logger.debug(resultados)
            if 'excel' in request.POST:
                logger.debug('Excel')
                target_stream = generateExcelNCR(resultados)
                response = HttpResponse(
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename="ReporteNCR.xlsx"'
                target_stream.flush()
                ret_excel = target_stream.getvalue()
                target_stream.close()
                response.write(ret_excel)
                return response
            if 'pdf' in request.POST:
                logger.debug('PDF')
                imagenes = listFotos(resultados)
                if "colores" in request.POST:
                    colores = True
                else:
                    colores = False
                fecha = datetime.strptime(request.POST['fecha'],'%d-%m-%Y').date()

                nombre_archivo = 'Sin'
                if request.POST['nombre'] != '':
                    nombre_archivo = request.POST['nombre']
                nombre = 'INFNCR_' + parque.codigo + '-' + nombre_archivo + '_' + fecha.strftime("%y%m%d") + '.pdf'

                respuesta = generatePdf(parque,resultados,imagenes,request.POST['titulo'],request,
                                        colores=colores,
                                        fecha=fecha,
                                        nombre = nombre,
                                        )
                respuesta['Content-Disposition'] = 'attachment; filename="' + nombre + '"'
                return respuesta

    return render(request, 'ncr/informeNCR.html',
        {'cont': contenido,
         'parque': parque,
         'aerogeneradores':aerogeneradores,
         'form':form,
         'resultados':resultados,
        })

def generatePdf(parque,resultados,imagenes, titulo,
                request = None,
                show_fotos=True,
                colores = True,
                fecha = date.today,
                nombre = ''):
    with open(os.path.join(settings.BASE_DIR, 'static/common/images/check-mark-3-64.gif'), "rb") as image_file:
        img_solucionado = base64.b64encode(image_file.read())
    with open(os.path.join(settings.BASE_DIR, 'static/common/images/x-mark-64-amarillo.gif'), "rb") as image_file:
        img_parcialsolucionado = base64.b64encode(image_file.read())
    with open(os.path.join(settings.BASE_DIR, 'static/common/images/x-mark-64.gif'), "rb") as image_file:
        img_nosolucionado = base64.b64encode(image_file.read())
    with open(os.path.join(settings.BASE_DIR, 'static/common/images/saroenlogo.png'), "rb") as image_file:
        logo_saroen = base64.b64encode(image_file.read())

    if request is not None:
        return render_to_pdf_response(request, 'ncr/punchlistPDF.html',
                                           {'pagesize': 'LETTER',
                                            'title': 'Reporte Punchlist',
                                            'resultados': resultados,
                                            'main_fotos': imagenes,
                                            'parque': parque,
                                            'titulo': titulo,
                                            'show_fotos': show_fotos,
                                            'img_solucionado': img_solucionado,
                                            'img_parcialsolucionado': img_parcialsolucionado,
                                            'img_nosolucionado': img_nosolucionado,
                                            'logo_saroen': logo_saroen,
                                            'colores' : colores,
                                            'fecha': fecha,
                                            'nombre': nombre,
                                            }, content_type='application/pdf',
                                           response_class=HttpResponse)
    else:
        pdf = render_to_pdf('ncr/punchlistPDF.html',
                            {'pagesize': 'LETTER',
                             'title': 'Reporte Punchlist',
                             'resultados': resultados,
                             'main_fotos': imagenes,
                             'parque': parque,
                             'titulo': titulo,
                             'show_fotos': show_fotos,
                             'img_solucionado': img_solucionado,
                             'img_parcialsolucionado': img_parcialsolucionado,
                             'img_nosolucionado': img_nosolucionado,
                             'logo_saroen': logo_saroen,
                             'colores': colores,
                             'fecha': fecha,
                             'nombre': nombre,
                             })
        return StringIO.StringIO(pdf)

def listFotos(resultados):
    main_fotos = {}
    for res in resultados:
        r=res.revision_set.all().order_by('-id')[0]
        results = Fotos.objects.filter(revision=r, principal=True)
        if results.count() > 0:
            main_fotos[res.id] = results[0].reporte_img.url
    return main_fotos

def punchlistResults(parque, aerogenerador, reparadas):

    resultados = Observacion.objects.filter(parque=parque, aerogenerador=aerogenerador, punchlist=True)
    if not reparadas:
        resultados = resultados.exclude(estado__nombre__exact='Solucionado').exclude(cerrado=True)
    main_fotos = listFotos(resultados)
    if aerogenerador.nombre == u'General':
        titulo = 'LISTADO DE OBSERVACIONES GENERALES'
    elif aerogenerador.nombre == u'Puerto':
        titulo = 'LISTADO DE OBSERVACIONES EN PUERTO'
    else:
        titulo = 'LISTADO DE PENDIENTES AEROGENERADOR ' + aerogenerador.nombre
    return [resultados, main_fotos, titulo]

def generateWord(parque, aerogenerador,reparadas):
    [resultados, main_fotos, titulo] = punchlistResults(parque, aerogenerador, reparadas)
    if parque.word:
        nombre_archivo = parque.word.file.name
    else:
        nombre_archivo = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/ncr/punchlist.docx'
    f = open(nombre_archivo, 'rb')
    document = Document(f)
    document._body.clear_content()

    section = document.sections[0]
    section.page_height = Mm(279.4)
    section.page_width = Mm(215.9)
    h = document.add_heading(titulo, 2)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    document.add_paragraph('')
    for s in document.styles.latent_styles.element:
        logger.debug(s.name)
    table = document.add_table(rows=1, cols=3, style="Punchlist")
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Item'
    hdr_cells[1].text = 'Componente'
    hdr_cells[2].text = u'Descripción'
    # styles = document.styles
    # table.rows[0].style = "borderColor:red;background-color:blue"

    for r in resultados:
        row_cells = table.add_row().cells
        row_cells[0].text = 'OBS_' + parque.codigo + '-' + r.aerogenerador.nombre + '-' + str(r.observacion_id)
        row_cells[1].text = r.componente.nombre
        row_cells[2].text = r.nombre
    document.add_page_break()
    h = document.add_heading(u'Fotografías', 2)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    table = document.add_table(rows=1, cols=2, style="Fotos")
    first = True
    idx = 0
    for r in resultados:
        if not first:
            if idx % 2 == 0:
                row_cells = table.add_row().cells
                celda = 0
            else:
                celda = 1
        else:
            row_cells = table.rows[0].cells
            first = False
            celda = 0
        idx = idx + 1
        logger.debug(main_fotos[r.id])
        archivo = settings.BASE_DIR + main_fotos[r.id]
        c = row_cells[celda].paragraphs[0]
        aux = c.add_run()
        aux.add_picture(archivo, width=Cm(7.5))
        p = row_cells[celda].add_paragraph()
        p.text = 'OBS_' + parque.codigo + '-' + r.aerogenerador.nombre + '-' + str(r.observacion_id) + ' '
        aux2 = p.add_run()
        if r.estado.nombre == 'Solucionado':
            status_img = os.path.join(settings.BASE_DIR, 'static/common/images/check-mark-3-64.gif')
        elif r.estado.nombre == 'Parcialmente Solucionado':
            status_img = os.path.join(settings.BASE_DIR, 'static/common/images/x-mark-64-amarillo.gif')
        elif r.estado.nombre == 'No Solucionado':
            status_img = os.path.join(settings.BASE_DIR, 'static/common/images/x-mark-64.gif')
        aux2.add_picture(status_img, width=Cm(0.4))
    target_stream = StringIO.StringIO()
    document.save(target_stream)
    return target_stream

@login_required(login_url='ingresar')
def punchlist(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Punchlist'
    contenido.subtitulo='Parque '+ parque.nombre
    contenido.menu = ['menu-ncr', 'menu2-punchlist']

    form = Punchlist(parque=parque)
    resultados = None

    show_fotos = False
    if request.method == 'POST':
        logger.debug('informePunchlist Post')
        form = Punchlist(request.POST, parque=parque)

        if form.is_valid():
            logger.debug("Form Valid")
            show_fotos = form.cleaned_data['fotos']
            if 'word' in request.POST:
                logger.debug('WORD')
                if len(form.cleaned_data['aerogenerador']) == 1:
                    ag = form.cleaned_data['aerogenerador'][0]
                    target_stream = generateWord(parque,ag,form.cleaned_data['reparadas'])
                    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    fecha_str = form.cleaned_data['fecha'].strftime("%y%m%d")
                    nombre = 'PL_' + parque.codigo + '-' + ag.nombre + '_' + fecha_str + '.docx'
                    response['Content-Disposition'] = 'attachment; filename='+nombre
                    target_stream.flush()
                    ret_word = target_stream.getvalue()
                    target_stream.close()
                    response.write(ret_word)
                    return response
                elif len(form.cleaned_data['aerogenerador']) > 1:
                    response = HttpResponse(content_type='application/zip')
                    response['Content-Disposition'] = 'filename=punchlistWord.zip'
                    buff = StringIO.StringIO()
                    archive = zipfile.ZipFile(buff, 'w', zipfile.ZIP_DEFLATED)

                    for ag in form.cleaned_data['aerogenerador']:
                        target_stream = generateWord(parque, ag, form.cleaned_data['reparadas'])
                        fecha_str = form.cleaned_data['fecha'].strftime("%y%m%d")
                        archivo_name = 'PL_' + parque.codigo + '-' + ag.nombre + '_' + fecha_str + '.docx'
                        logger.debug(archivo_name)
                        archive.writestr(archivo_name, target_stream.getvalue())
                    archive.close()
                    buff.flush()
                    ret_zip = buff.getvalue()
                    buff.close()
                    response.write(ret_zip)
                    return response
            else:
                if len(form.cleaned_data['aerogenerador']) == 1:
                    ag = form.cleaned_data['aerogenerador'][0]
                    [resultados, main_fotos, titulo] = punchlistResults(parque,ag,form.cleaned_data['reparadas'])
                    logger.debug(resultados)
                    colores = form.cleaned_data['colores']
                    fecha_str = form.cleaned_data['fecha'].strftime("%y%m%d")
                    nombre = 'PL_' + parque.codigo + '-' + ag.nombre + '_' + fecha_str + '.pdf'
                    respuesta = generatePdf(parque,resultados,main_fotos,titulo,request,
                                            show_fotos=show_fotos,
                                            colores=colores,
                                            fecha=form.cleaned_data['fecha'],
                                            nombre=nombre)
                    respuesta['Content-Disposition'] = 'attachment; filename='+nombre
                    return respuesta
                elif len(form.cleaned_data['aerogenerador']) > 1:
                    response = HttpResponse(content_type='application/zip')
                    response['Content-Disposition'] = 'filename=punchlistPDF.zip'
                    buff = StringIO.StringIO()
                    archive = zipfile.ZipFile(buff, 'w', zipfile.ZIP_DEFLATED)

                    for ag in form.cleaned_data['aerogenerador']:
                        [resultados, main_fotos, titulo] = punchlistResults(parque, ag, form.cleaned_data['reparadas'])
                        logger.debug(resultados)
                        colores = form.cleaned_data['colores']
                        fecha_str = form.cleaned_data['fecha'].strftime("%y%m%d")
                        archivo_name = 'PL_' + parque.codigo + '-' + ag.nombre + '_' + fecha_str + '.pdf'
                        archivo = generatePdf(parque, resultados, main_fotos, titulo,
                                              show_fotos=show_fotos,
                                              colores = colores,
                                              fecha=form.cleaned_data['fecha'],
                                              nombre=archivo_name)

                        logger.debug(archivo_name)
                        archive.writestr(archivo_name, archivo.getvalue())
                    archive.close()
                    buff.flush()
                    ret_zip = buff.getvalue()
                    buff.close()
                    response.write(ret_zip)
                    return response


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
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Listado de inspectores'
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
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
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
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
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
    aerogeneradores = Aerogenerador.objects.filter(parque=parque).order_by('idx')
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