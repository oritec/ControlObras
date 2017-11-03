from usuarios.models import Usuario
from usuarios.views import usuario_cambiarcontrasena
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

class ChangePasswordMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        user = request.user
        if not user.is_anonymous:
            usuario = Usuario.objects.get(user=user)

            if not usuario.changed_pass:
                return usuario_cambiarcontrasena(request)

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response


class PermissionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_template_response(self,request,response):
        if 'parque' in response.context_data:
            user = request.user
            if not user.is_anonymous:
                usuario = Usuario.objects.get(user=user)
                if response.context_data['parque'] not in usuario.parques.all():
                    return TemplateResponse(request, '403.html')
        return response