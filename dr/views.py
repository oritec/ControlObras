# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.template.response import TemplateResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from vista.functions import *
from django.shortcuts import get_object_or_404
from vista.models import ParqueSolar, Aerogenerador
from usuarios.models import Log
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from dr.forms import DRForm
from dr.models import DR, ActividadDR, ComposicionDR, FotosDR
from django.core.exceptions import PermissionDenied
import os
import StringIO
from django.http import HttpResponse
from docx import Document
from docx.shared import Mm, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE

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

    drs = DR.objects.filter(parque=parque)

    return TemplateResponse(request, 'dr/listado.html',
                            {'cont': contenido,
                             'parque': parque,
                             'aerogeneradores': aerogeneradores,
                             'filas': drs
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
            #dr.save() # Necesario para actualizar campos
            return HttpResponseRedirect(reverse('dr:editar', args=[parque.slug,dr.id]))
        else:
            logger.debug('Formulario no es válido...')

    if form is None:
        aux = DR.objects.filter(parque=parque).order_by('-numero')
        if aux.exists():
            next_num = aux[0].numero + 1
        else:
            next_num = 1
        form = DRForm(initial={'parque':parque.id, 'numero': next_num})

    return TemplateResponse(request, 'dr/agregar.html',
                            {'cont': contenido,
                             'parque': parque,
                             'aerogeneradores': aerogeneradores,
                             'form': form,
                             'back_url': reverse('dr:listado', args=[parque.slug])
                             })

@login_required(login_url='ingresar')
def editar(request, slug, dr_id):
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
        form = DRForm(request.POST, instance=dr)
        if form.is_valid():
            logger.debug('Formulario válido.')
            dr = form.save()
            log_msg = "Se agrega reporte diario para parque " + parque.nombre
            log = Log(texto=log_msg, tipo=1, user=request.user)
            log.save()
            #return HttpResponseRedirect(reverse('dr:observaciones-show', args=[parque.slug,observacion.id]))
        else:
            logger.debug('Formulario no es válido...')

    if form is None:
        form = DRForm(instance=dr)

    return TemplateResponse(request, 'dr/editar.html',
                            {'cont': contenido,
                             'parque': parque,
                             'aerogeneradores': aerogeneradores,
                             'form': form,
                             'editar': True,
                             'dr': dr,
                             'back_url': reverse('dr:listado', args=[parque.slug])
                             })

@login_required(login_url='ingresar')
def borrar(request, slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)

    if request.method == 'POST':
        logger.debug('POST del_dr')
        dr=DR.objects.get(id=int(request.POST['del_id']))
        if not (request.user.has_perm('ncr.delete_revision') or request.user == dr.created_by) :
            raise PermissionDenied

        log_msg = "Se elimina DR para parque " + parque.nombre + \
                  " - ID - " + str(dr.id)

        dr.delete()
        log = Log(texto=log_msg, tipo=3, user=request.user)
        log.save()

        return HttpResponseRedirect(request.POST['back_url'])

@login_required(login_url='ingresar')
def actividad_agregar(request, slug, dr_id):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    dr = get_object_or_404(DR, id=dr_id)
    if request.method == 'POST':
        if 'actividad_descripcion' in request.POST:
            log_msg = "Se agrega Actividad para parque " + parque.nombre + \
                      " - DR - " + str(dr.id)
            actividad = ActividadDR(descripcion=request.POST['actividad_descripcion'],dr=dr)
            actividad.save()
            log = Log(texto=log_msg, tipo=3, user=request.user)
            log.save()
        return HttpResponseRedirect(reverse('dr:editar', args=[parque.slug,dr.id]))

@login_required(login_url='ingresar')
def composicion_agregar(request, slug, dr_id):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    dr = get_object_or_404(DR, id=dr_id)
    if request.method == 'POST':
        if 'actividad_descripcion' in request.POST:
            log_msg = "Se agrega Actividad para parque " + parque.nombre + \
                      " - DR - " + str(dr.id)
            actividad = ActividadDR(descripcion=request.POST['actividad_descripcion'],dr=dr)
            actividad.save()
            log = Log(texto=log_msg, tipo=3, user=request.user)
            log.save()
        elif 'act_id' in request.POST:
            actividad = get_object_or_404(ActividadDR,id=request.POST['act_id'])
            composicion = ComposicionDR(actividad=actividad,
                                        pie=request.POST['composicion_pie'],
                                        tipo=request.POST['pattern'])
            composicion.save()
            nofotos = int(request.POST['nofotos'])
            for i in range(nofotos):
                file_field = 'file_input_' + request.POST['pattern'] + '_' + str(i+1)
                if file_field in request.FILES:
                    f = FotosDR(composicion=composicion,
                                imagen=request.FILES[file_field],
                                orden=i)
                    f.save()
        return HttpResponseRedirect(reverse('dr:editar', args=[parque.slug,dr.id]))

@login_required(login_url='ingresar')
def create_dr_word(request, slug,dr_id):
    dr = get_object_or_404(DR, id=dr_id)
    nombre_archivo = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/dr/dr.docx'
    f = open(nombre_archivo, 'rb')
    document = Document(f)
    document._body.clear_content()
    temp_doc = Document()
    #document.styles.add_style('ListBullet', temp_doc.styles['ListBullet'].type)
    #document.styles.add_style('List Paragraph', temp_doc.styles['List Paragraph'].type)

    section = document.sections[0]
    section.page_height = Mm(279.4)
    section.page_width = Mm(215.9)
    for s in temp_doc.styles.latent_styles.element:
        logger.debug(s.name)
    table = document.add_table(rows=1, cols=3, style="Titulo")

    row_cells = table.rows[0].cells
    #table.rows[0].height_rule = WD_ROW_HEIGHT.EXACTLY
    tr = table.rows[0]._tr
    trPr = tr.get_or_add_trPr()
    trHeight = OxmlElement('w:trHeight')
    trHeight.set(qn('w:val'), "800")
    trHeight.set(qn('w:hRule'), "atLeast")
    trPr.append(trHeight)
    row_cells[1].paragraphs[0].add_run('INFORME DIARIO').bold = True
    logo_archivo = settings.BASE_DIR + '/static/common/images/saroenlogo-excel.png'
    r = row_cells[0].paragraphs[0].add_run()
    r.add_picture(logo_archivo, width=Cm(4.5))
    document.add_paragraph('')
    logo_empresa = dr.parque.logo.file.name
    r = row_cells[2].paragraphs[0].add_run()
    r.add_picture(logo_empresa, width=Cm(4.5))
    document.add_paragraph('')
    # Información del reporte
    table = document.add_table(rows=1, cols=4, style="Titulo")
    row_cells = table.rows[0].cells
    row_cells[0].paragraphs[0].add_run('Proyecto:').bold = True
    row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
    row_cells[1].paragraphs[0].add_run(dr.parque.nombre).bold = True
    row_cells[2].paragraphs[0].add_run('Fecha:').bold = True
    row_cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
    row_cells[3].paragraphs[0].add_run(dr.fecha.strftime("%d/%m/%Y")).bold = True

    row_cells = table.add_row().cells
    row_cells[0].paragraphs[0].add_run('Cliente:').bold = True
    row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
    row_cells[1].paragraphs[0].add_run(dr.parque.cliente).bold = True
    row_cells[2].paragraphs[0].add_run('Informe Nº:').bold = True
    row_cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
    row_cells[3].paragraphs[0].add_run('DR_' + dr.parque.codigo.upper() + '-' + str(dr.numero)).bold = True

    row_cells = table.add_row().cells
    row_cells[0].paragraphs[0].add_run('WTG Num:').bold = True
    row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
    row_cells[1].paragraphs[0].add_run(dr.sitio)
    row_cells[2].paragraphs[0].add_run('Climatología:')
    row_cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
    row_cells[3].paragraphs[0].add_run(dr.climatologia)

    row_cells = table.add_row().cells
    r = row_cells[0]
    for idx in range(1,4):
        r = r.merge(row_cells[idx])

    row_cells = table.add_row().cells
    row_cells[0].paragraphs[0].add_run('Actividades:').bold = True
    row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
    row_cells[1].paragraphs[0].add_run(dr.actividades)
    #row_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = row_cells[1]
    for idx in range(2,4):
        r = r.merge(row_cells[idx])

    row_cells = table.add_row().cells
    r = row_cells[0]

    for actividad in dr.actividaddr_set.all():
        p = r.add_paragraph(actividad.descripcion)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        #p.text = 'Inspección final'
        p.style = 'ListaParrafo'

    p = r.add_paragraph()
    for idx in range(1, 4):
        r = r.merge(row_cells[idx])

    document.add_paragraph('')
    # Inserta fotos
    foto_count = 1
    for actividad in dr.actividaddr_set.all():
        for composicion in actividad.composiciondr_set.all():
            if composicion.tipo == '1V2H':
                table = document.add_table(rows=2, cols=2, style="TablaFotos")
                row_cells = table.rows[0].cells
                # foto 1
                foto = FotosDR.objects.get(composicion=composicion, orden=0)
                foto_filename = settings.BASE_DIR + foto.imagen.url
                r = row_cells[0].paragraphs[0].add_run()
                r.add_picture(foto_filename, width=Mm(90), height=Mm(120))
                cell_toadd = row_cells[0]
                # foto 2
                foto = FotosDR.objects.get(composicion=composicion, orden=1)
                foto_filename = settings.BASE_DIR + foto.imagen.url
                r = row_cells[1].paragraphs[0].add_run()
                r.add_picture(foto_filename, width=Mm(79), height=Mm(59.1))
                # foto 3
                row_cells = table.rows[1].cells
                foto = FotosDR.objects.get(composicion=composicion, orden=2)
                foto_filename = settings.BASE_DIR + foto.imagen.url
                r = row_cells[1].paragraphs[0].add_run()
                r.add_picture(foto_filename, width=Mm(79), height=Mm(59.1))
                cell_toadd.merge(row_cells[0])
                p = document.add_paragraph('Ilustración ' + str(foto_count) + '. ' + composicion.pie)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.style = 'Pie'
                foto_count += 1
    target_stream = StringIO.StringIO()
    document.save(target_stream)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    fecha_str = datetime.datetime.now().strftime("%y%m%d")
    nombre = 'DR_' + fecha_str + '.docx'
    response['Content-Disposition'] = 'attachment; filename=' + nombre
    target_stream.flush()
    ret_word = target_stream.getvalue()
    target_stream.close()
    response.write(ret_word)
    return response
