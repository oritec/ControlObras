# -*- coding: utf-8 -*-
from django.shortcuts import render

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context
from django.contrib.auth.models import User
from usuarios.models import Usuario
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required

from django.contrib.auth import login, authenticate, logout
from usuarios.form import EditUsuarioForm, NewUsuarioForm, ChangePasswordForm
from django.contrib.auth.models import Group
from django.contrib import messages
from vista.models import ParqueSolar
from models import Log
#Helpers
from vista.functions import *

import datetime
import logging
import os.path
logger = logging.getLogger('oritec')
#logger.setLevel(logging.DEBUG)

from usuarios.form import LoginForm

def check_password(user):
    usuario = Usuario.objects.get(user=user)
    return usuario.changed_pass

def check_permisos(user):
    usuario = Usuario.objects.get(user=user)
    if user.is_superuser:
        return True
    else:
        return False

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

def home(request):
    contenido = ContenidoContainer()
    contenido.user = request.user
    contenido.titulo = u'Perfil Usuario'
    contenido.subtitulo = ''
    contenido.menu = ['menu-perfil', 'menu2-dashboard']
    usuario = Usuario.objects.get(user=request.user)
    proyectos = usuario.parques.all()

    logs = Log.objects.filter(user=request.user).order_by('-created_at')[:10]
    logs_all = Log.objects.all().order_by('-created_at')[:20]
    return render(request, 'usuarios/home.html',
                  {'cont': contenido,
                   'proyectos': proyectos,
                   'logs': logs,
                   'logs_all': logs_all,
                   })

@permission_required('usuarios.add_usuario', raise_exception=True)
def usuarios(request):
    contenido = ContenidoContainer()
    contenido.user = request.user
    contenido.titulo = u'Administración de usuarios'
    contenido.subtitulo = ''
    contenido.menu = ['menu-usuarios', 'menu2-dashboard']
    users = Usuario.objects.all()
    return render(request, 'usuarios/usuarios.html',
                  {'cont': contenido,
                   'usuarios': users,
                   })

def check_permissions(usuario, perfil, proyectos=None,user_edit=None):
    user = usuario.user
    if user.is_superuser:
        return True

    group = Group.objects.get(name='Usuario 1')
    # Primer check, el unico otro usuario que puede hacer algo es el Usuario 1.
    if not group in user.groups.all():
        return False
    if perfil == 0:
        return False  # No puede crear un usuario con acceso a superusuario
    elif perfil == group.id:
        return False  # No puede crear un usuario con su mismo perfil.
    if user_edit is not None:
        if user_edit.user.is_superuser:
            return False # No puede Editar una caracteristica de un superusuario
        if group in user_edit.user.groups.all():
            return False # No puede Editar a un usuario de su mismo nivel

    if proyectos is not None:
        if user_edit is None:
            cambiados = proyectos
        else:
            eliminados = []
            old_int = user_edit.parques.all()
            old = []
            for o in old_int:
                old.append(str(o.id))
                if str(o.id) not in proyectos:
                    eliminados.append(str(o.id))
            nuevos = []
            for n in proyectos:
                if n not in old:
                    nuevos.append(n)
            cambiados = eliminados + nuevos
        posibles = []
        for p in usuario.parques.all():
            posibles.append(str(p.id))
        for c in cambiados:
            if c not in posibles:
                return False
    return True

def set_user_information(user,user_edit,form):
    if user_edit is None:
        if form.cleaned_data['perfil'] == '0':
            user_django_new = User.objects.create_superuser(form.cleaned_data['nombre'],
                                                            None,
                                                            form.cleaned_data['password'])
        else:
            user_django_new = User.objects.create_user(form.cleaned_data['nombre'],
                                                       None,
                                                       form.cleaned_data['password'])
        user_edit = Usuario(user=user_django_new)
        user_edit.save()
    else:
        user_edit.user.username = form.cleaned_data['nombre']

    user_django = user_edit.user
    if form.cleaned_data['perfil'] == '0':
        user_django.is_superuser = True
        user_edit.parques.clear()
        for parque in ParqueSolar.objects.all():
            user_edit.parques.add(parque)
    else:
        grupo = Group.objects.get(id=int(form.cleaned_data['perfil']))
        user_django.groups.clear()
        user_django.groups.add(grupo)
        user_django.is_superuser = False
        user_edit.parques.clear()
        for p_id in form.cleaned_data['proyectos']:
            parque = ParqueSolar.objects.get(id=int(p_id))
            user_edit.parques.add(parque)

    user_django.save()
    user_edit.save()

    return True

@permission_required('usuarios.add_usuario', raise_exception=True)
def usuario_editar(request, usuario_id):
    contenido = ContenidoContainer()
    contenido.user = request.user
    usuario = Usuario.objects.get(user=request.user)
    usuario_edit = Usuario.objects.get(id=usuario_id)

    contenido.titulo = u'Administración de usuarios'
    contenido.subtitulo = 'Editar usuario'
    contenido.menu = ['menu-usuarios', 'menu2-dashboard']
    form = None
    valid = False
    if request.method == 'POST':
        form = EditUsuarioForm(request.POST,usuario=usuario)
        if form.is_valid():
            proyectos_add = []
            check = check_permissions(usuario, form.cleaned_data['perfil'], proyectos=form.cleaned_data['proyectos'],user_edit = usuario_edit)
            if not check:
                messages.add_message(request, messages.ERROR, 'Usuario no tiene permisos para realizar esta acción.')
            else:
                valid = set_user_information(request.user, usuario_edit, form)
                if valid:
                    log_msg = "Se edita usuario " + usuario_edit.user.username
                    log = Log(texto=log_msg, tipo=2, user=request.user)
                    log.save()
                    messages.add_message(request, messages.SUCCESS, 'Usuario modificado con éxito!')

        if not valid:
            messages.add_message(request, messages.ERROR, 'Edición de usuario fallida.')
    if form is None:
        form = EditUsuarioForm(usuario=usuario,edit= usuario_edit)
    if valid:
        return HttpResponseRedirect(reverse('usuarios:usuarios'))
    return render(request, 'usuarios/usuario_agregar.html',
                  {'cont': contenido,
                   'form':form,
                   })

@permission_required('usuarios.add_usuario', raise_exception=True)
def usuario_agregar(request):
    contenido = ContenidoContainer()
    contenido.user = request.user
    usuario=Usuario.objects.get(user=request.user)
    contenido.titulo = u'Administración de usuarios'
    contenido.subtitulo = 'Agregar Usuario'
    contenido.menu = ['menu-usuarios', 'menu2-dashboard']

    form = None
    valid = False

    if request.method == 'POST':
        form = NewUsuarioForm(request.POST,usuario=usuario)
        if form.is_valid():
            check = check_permissions(usuario, form.cleaned_data['perfil'],
                                      proyectos=form.cleaned_data['proyectos'])
            if not check:
                messages.add_message(request, messages.ERROR, 'Usuario no tiene permisos para realizar esta acción.')
            else:
                valid = set_user_information(request.user, None, form)
                if valid:
                    log_msg = "Se agrega usuario " + form.cleaned_data['nombre']
                    log = Log(texto=log_msg, tipo=1, user=request.user)
                    log.save()
                    messages.add_message(request, messages.SUCCESS, 'Usuario agregado con éxito!')
        else:
            if '__all__' in form.errors:
                for error in form.errors['__all__']:
                    messages.add_message(request, messages.ERROR, error)

        if not valid:
            messages.add_message(request, messages.ERROR, 'No se pudo agregar usuario.')

    if form is None:
        form = NewUsuarioForm(usuario=usuario)

    if valid:
        return HttpResponseRedirect(reverse('usuarios:usuarios'))

    return render(request, 'usuarios/usuario_agregar.html',
                  {'cont': contenido,
                   'form':form,
                   })

@permission_required('usuarios.add_usuario', raise_exception=True)
def usuario_borrar(request):
    contenido = ContenidoContainer()
    contenido.user = request.user
    contenido.titulo = u'Administración de usuarios'
    contenido.subtitulo = ''
    contenido.menu = ['menu-usuarios', 'menu2-dashboard']
    if request.method == 'POST':
        usuario_del = Usuario.objects.get(id=request.POST['del_id'])

        if not request.user.is_superuser:
            messages.add_message(request, messages.ERROR, 'Usuario no tiene permisos para realizar esta acción.')
        else:
            log_msg = "Se elimina usuario " + usuario_del.user.username
            log = Log(texto=log_msg, tipo=3, user=request.user)
            usuario_del.user.delete()
            usuario_del.delete()
            log.save()
            messages.add_message(request, messages.SUCCESS, 'Usuario eliminado con éxito.')

    return HttpResponseRedirect(reverse('usuarios:usuarios'))

def usuario_cambiarcontrasena(request):
    contenido = ContenidoContainer()
    contenido.user = request.user
    contenido.titulo = u'Administración de usuario'
    contenido.subtitulo = 'Cambiar contraseña'
    contenido.menu = ['menu-contrasena', 'menu2-dashboard']

    form = None
    valid = False
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['password'])
            request.user.save()
            usuario = Usuario.objects.get(user=request.user)
            usuario.changed_pass = True
            usuario.save()
            log_msg = "Cambio de contraseña"
            log = Log(texto=log_msg, tipo=2, user=request.user)
            log.save()
            valid = True
            messages.add_message(request, messages.SUCCESS, 'Contraseña modificada con éxito!')
        else:
            if '__all__' in form.errors:
                for error in form.errors['__all__']:
                    messages.add_message(request, messages.ERROR, error)

    if form is None:
        form = ChangePasswordForm()

    if valid:
        return HttpResponseRedirect('/')
    return render(request, 'usuarios/change_password.html',
                  {'cont': contenido,
                   'form': form,
                   })

def usuario_forbidden(request):
    return render(request, 'vista/403.html')