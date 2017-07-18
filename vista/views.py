from django.shortcuts import render
from vista.functions import *

import logging
logger = logging.getLogger('oritec')

def index(request):
    contenido=ContenidoContainer()
    contenido.user=request.user
    contenido.titulo=u'Sistema'
    contenido.subtitulo=u'Oritec'
    contenido.menu = ['menu-principal', 'menu2-resumen']


    return render(request, 'vista/index.html',
        {'cont': contenido,
        })