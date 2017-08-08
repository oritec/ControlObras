from django import template
from django.conf import settings
from django.core.urlresolvers import resolve
from datetime import date, timedelta, datetime
from dateutil import relativedelta
from pytz import timezone
import pytz
from django.utils.dateparse import parse_datetime

import logging
logger = logging.getLogger('oritec')

register = template.Library()

@register.filter
def get_range( value,arg ):
    #logger.debug(range(value,arg))
    return range( value,arg )

@register.filter()
def to_int(value):
    return int(value)

@register.filter()
def to_fecha(value):
    if int(value.year)==1900:
        return "Indefinido"
    elif int(value.year) < 2043:
        return value.strftime("%d/%m/%Y")
    else:
        return "Indefinido"
    
@register.filter()
def to_fecha_contrato(value):
        return value.strftime("%d/%m/%Y")

@register.simple_tag
def complete_url_photo(name, arg):
    if arg=='dmh':
        return 'http://'+getattr(settings, 'DATABASES')['dmhdata']['HOST']+':180/CMS/PhotoID/ProcessedImages/'+name
    elif arg=='drt':
        return 'http://'+getattr(settings, 'DATABASES')['drtdata']['HOST']+':180/CMS/PhotoID/ProcessedImages/'+name

@register.simple_tag
def complete_url_photo_alt(name,arg):
    if arg=='dmh':
        return 'http://'+getattr(settings, 'DATABASES')['dmhdata']['HOST']+':180/CMS/PhotoID/HolderImages/'+name
    elif arg=='drt':
        return 'http://'+getattr(settings, 'DATABASES')['drtdata']['HOST']+':180/CMS/PhotoID/HolderImages/'+name

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_attr(queryitem, key):
    return getattr(queryitem,key)

@register.filter 
def get_verbose_name(queryitem,key):
    return queryitem._meta.get_field(key).verbose_name.title()

@register.filter
def get_class(ob):
    return ob.field.widget.__class__.__name__

@register.filter
def get_model_name(value):
    return value.__class__.__name__

@register.filter    
def subtract(value, arg):
    return value - arg

@register.filter
def tipo(value):
    return str(type(value))

@register.filter
def to_month(value):
    MESES={1:'Enero',2:'Febrero',3:'Marzo',4:'Abril',5:'Mayo',6:'Junio',7:'Julio',8:'Agosto',9:'Septiembre',
           10:'Octubre',11:'Noviembre',12:'Diciembre'}
    return MESES.get(value)

@register.filter
def to_month_year(value):
    MESES={1:'Enero',2:'Febrero',3:'Marzo',4:'Abril',5:'Mayo',6:'Junio',7:'Julio',8:'Agosto',9:'Septiembre',
           10:'Octubre',11:'Noviembre',12:'Diciembre'}
    return MESES.get(value.month) +" " + str(value.year)

@register.filter
def get_age(value):
    if value != 0:
        today = date.today()
        return today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    else:
        return ""

@register.filter()
def to_thousands(value):
    return '{:,}'.format(value).replace(",", ".")

@register.filter()
def get_altfoto(value):
    return "common/images/incognito.jpg"
    if value.genero=='H':
        return "common/images/socio.jpg"
    else:
        return "common/images/socia.jpg"

@register.filter    
def restar_meses(value, meses):
    return value - relativedelta.relativedelta(months=meses)

@register.filter
def link_dashboard(evento):
    gmt = timezone("UTC")
    utc = pytz.utc
    local = timezone("America/Santiago")
    #logger.debug(evento.inicio.strftime("%Y-%m-%d %H:%M:%S"))

    naive = parse_datetime(evento.inicio.strftime("%Y-%m-%d %H:%M:%S"))
    #logger.debug(local.localize(naive))
    inicio = local.localize(naive) - timedelta(seconds=3000)

    naive = parse_datetime(evento.final.strftime("%Y-%m-%d %H:%M:%S"))
    #logger.debug(local.localize(naive))
    final = local.localize(naive) + timedelta(seconds=3000)

    base="http://rakihuajache-demo.com:3000/dashboard/db/aerogenerador-"+evento.turbina[-1]

    dates = "?from=" + inicio.strftime('%s')+ "000" + "&to=" + final.strftime('%s') + "000"
    return base + dates

@register.filter
def link_dashboard2(evento):
    gmt = timezone("UTC")
    utc = pytz.utc
    local = timezone("America/Santiago")
    #logger.debug(evento.inicio.strftime("%Y-%m-%d %H:%M:%S"))

    naive = parse_datetime(evento.inicio.strftime("%Y-%m-%d %H:%M:%S"))
    #logger.debug(local.localize(naive))
    inicio = local.localize(naive) - timedelta(seconds=3000)

    naive = parse_datetime(evento.final.strftime("%Y-%m-%d %H:%M:%S"))
    #logger.debug(local.localize(naive))
    final = local.localize(naive) + timedelta(seconds=3000)

    base="https://snapshot.raintank.io/dashboard/snapshot/M0ArdqgIzEGw7F4NXXCIAmyMJw661kqB"

    dates = "?panelId=4&from=" + inicio.strftime('%s')+ "000" + "&to=" + final.strftime('%s') + "000"
    return base + dates

@register.filter
def seconds2printable(sec):
    return str(timedelta(seconds=int(sec))).replace("day","dia").replace("days","dias")

@register.filter
def multiply(value, arg):
    return value*arg

@register.filter
def divide(value, arg):
    return value/arg

@register.filter()
def filter_ag_id(value,arg):
    f=value.filter(id=int(arg))
    if f.count() > 0:
        return f[0].nombre
    else:
        return ''

@register.filter()
def filter_ag_idx(value,arg):
    f=value.filter(idx=int(arg))
    if f.count() > 0:
        return f[0].nombre
    else:
        return ''
