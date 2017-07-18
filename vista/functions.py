import logging
# Get an instance of a logger
logger = logging.getLogger('oritec')
import datetime

class ContenidoContainer:
    def __init__(self, titulo=''):
        self.titulo=titulo
        self.subtitulo=''
        self.titulotabla=''
        self.titulosubtabla=''
        self.user=None
        self.tablafields=[]
        self.showAdd=True
        self.edit=False
        self.showAccion=True
        self.isPopup=False
        self.menu=[]
        self.formOtro=False
        self.anchoVentana=400
        self.showpdf=False
        self.valorInventario=0
        self.tabs=[]
        self.toastrMsg=''
        self.toastrStatus=''

class RegistroContainer:
    def __init__(self, nombre='',apellido=''):
        self.nombre=nombre
        self.apellido=apellido
        self.cardnumber=0
        self.fecha=datetime.datetime.now()
        self.bus=''
        self.status=''
        self.sentido=''
        self.empresa=''
        
class ListaImportacion:
    def __init__(self, nombre='',apellido='', rut='', monto='', telefono='',email=''):
        self.nombre=nombre
        self.apellido=apellido
        self.rut=rut
        self.monto=monto
        self.telefono=telefono
        self.email=email
        
class LogImportar:
    def __init__(self, nombre='', rut='', mensaje=''):
        self.nombre=nombre
        self.rut=rut
        self.mensaje=mensaje
