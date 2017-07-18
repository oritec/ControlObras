from django.shortcuts import render

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context
from django.contrib.auth.models import User
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required

from django.contrib.auth import login, authenticate, logout

#Helpers
from vista.functions import *

import datetime
import logging
import os.path
logger = logging.getLogger('oritec')
#logger.setLevel(logging.DEBUG)

from usuarios.form import LoginForm

# ========== Login ==========
def ingresar(request, homepage):
    logger.debug(homepage)
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse(homepage))
    
    form = LoginForm(request.POST or None)
    
    if request.method=='POST' and form.is_valid():
        user = form.login(request)
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse(homepage))
    
    return render(request,'usuarios/login.html',
          {'form': form})

# ========== Logout ==========
def salir(request):
    logout(request)
    return HttpResponseRedirect(reverse('ingresar'))
