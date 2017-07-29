# -*- coding: utf-8 -*-
from django.shortcuts import render
from vista.functions import *
from django.contrib.auth.decorators import login_required, permission_required
from forms import ParqueForm, ParqueFormFull
from models import ParqueSolar
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect

import logging
logger = logging.getLogger('oritec')

@login_required(login_url='ingresar')
def index(request):
    parques=ParqueSolar.objects.all()
    formAddParque = ParqueForm()
    if request.method == 'POST':
        if 'addParque' in request.POST:
            formParque = ParqueForm(request.POST)
            if formParque.is_valid():
                formParque.save()
    return render(request, 'vista/index.html',
                  {'parques': parques,
                   'formAddParque': formAddParque})

@login_required(login_url='ingresar')
def home(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Parque Eólico'
    contenido.subtitulo=parque.nombre
    contenido.menu = ['menu-principal', 'menu2-resumen']

    return render(request, 'vista/home.html',
        {'cont': contenido,
         'parque': parque,
        })

@login_required(login_url='ingresar')
def del_parque(request):
    if request.method == 'POST':
        if 'parque' in request.POST:
            aux = ParqueSolar.objects.get(slug__exact=request.POST['parque'])
            aux.delete()
    return HttpResponseRedirect(reverse('vista:index'))

@login_required(login_url='ingresar')
def configuracion(request,slug):
    parque = get_object_or_404(ParqueSolar, slug=slug)
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Parque Eólico'
    contenido.subtitulo=parque.nombre
    contenido.menu = ['menu-principal', 'menu2-configuracion']
    form = None
    if request.method == 'POST':
        form = ParqueFormFull(request.POST, instance=parque)
        if form.is_valid():
            logger.debug("Formulario es válido")
            parque = form.save()
            mensaje = 'Información modificada con éxito'
            messages.add_message(request, messages.SUCCESS, mensaje)
            response = redirect('vista:home', slug=parque.slug)
            ParqueSolar.objects.update()
            return response
        else:
            logger.debug(form.errors)
            contenido.toastrStatus = "error"
            contenido.toastrMsg = "Información no se ha guardado. Revise el formulario nuevamente."

    if form is None:
        form = ParqueFormFull(instance=parque)

    return render(request, 'vista/configuracion.html',
        {'cont': contenido,
         'parque': parque,
         'form': form,
        })