# -*- coding: utf-8 -*-
from django.shortcuts import render
from vista.functions import *
from django.contrib.auth.decorators import login_required, permission_required
from forms import ParqueChoiceForm,ParqueForm
from models import ParqueSolar
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

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
        })

@login_required(login_url='ingresar')
def del_parque(request):
    if request.method == 'POST':
        if 'parque' in request.POST:
            aux = ParqueSolar.objects.get(slug__exact=request.POST['parque'])
            aux.delete()
    return HttpResponseRedirect(reverse('vista:index'))
