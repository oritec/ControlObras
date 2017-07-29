"""BaseSistemas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from usuarios.views import ingresar, salir
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', ingresar, {'homepage':'vista:index'}, name='ingresar'),
    url(r'^logout/$', salir, name='salir'),
    url(r'^(?P<slug>[-\w\d]+)/ncr/',include('ncr.urls', namespace='ncr', app_name="ncr")),
    url(r'^',include('vista.urls', namespace='vista', app_name="vista")),
]