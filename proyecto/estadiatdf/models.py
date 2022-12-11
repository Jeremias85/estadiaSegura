from django.db import models
from django.contrib.auth.models import User
# from datetime import date, time
from datetime import date

import uuid
# from django.db.models.fields.mixins import FieldCacheMixin
# from django.db.models.fields.related import ForeignObject
# from django.http import HttpResponseRedirect
# from django.urls import reverse


#from django.views.generic.detail import SingleObjectTemplateResponseMixin

def crearToken():
    return uuid.uuid4()

class Alojamiento(models.Model):
    responsable = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    suit_id = models.IntegerField(blank=True, null=True)
    nombre = models.CharField(max_length=100, blank = True, null = True)
    domicilio = models.CharField(max_length=100, blank = True, null = True)
    localidad = models.CharField(max_length=50, blank = True, null = True)
    cuit = models.BigIntegerField(blank=True, null=True)
    image_url = models.CharField(max_length=100, blank = True, null = True)
    #fecha_actualizacion = models.DateTimeField(blank=True, null=True)
    token = models.CharField(max_length=40, null = True, default=None)
    #Forma correcta de indicar campo token uuid4
    #token = models.UUIDField(default=uuid.uuid4, unique=True, editable=True, blank=True, null=True) 
    # Cada vez que se crea un establecimiento se genera un token de 32 caracteres (y 4 guiones)

    def __str__(self):
        return self.nombre

class Contacto(models.Model):
    tipo = models.CharField(max_length=20, blank = True, null = True)
    valor = models.CharField(max_length=100, blank = True, null = True)
    alojamiento = models.ForeignKey('Alojamiento', on_delete=models.CASCADE,)
    def __str__(self):
        return (self.alojamiento.nombre+" - "+self.valor)

class Reserva(models.Model):
    ESTADOS = (('Activa','Activa'),
              ('Finalizada','Finalizada'),
              ('Cancelada','Cancelada'),)
    alojamiento = models.ForeignKey('Alojamiento', on_delete=models.CASCADE)
    nombre_huesped = models.CharField(max_length=50, verbose_name='Nombre del huésped')
    origen_reserva = models.CharField(max_length=50, blank = True, null = True, verbose_name='Origen de la reserva')
    codigo_reserva = models.CharField(max_length=50, blank = True, null = True, verbose_name='Código de la reserva') # No integer porque puede haber letras
    fecha_check_in = models.DateField(verbose_name='Fecha de Check-in')
    fecha_check_out = models.DateField(verbose_name='Fecha de Check-out')
    fecha_reservado = models.DateField(verbose_name='Fecha de reserva', auto_now_add=True)
    pax = models.IntegerField(verbose_name='Pax')
    ingreso_rapido = models.BooleanField(verbose_name='Ingreso rápido', default=False)
    token = models.CharField(max_length=40, default=crearToken)
    comentario = models.CharField(verbose_name='Comentario', max_length=50, blank = True, null = True)
    estado = models.CharField(max_length=10, choices=ESTADOS, verbose_name='Estado de reserva', default='Activa')

    def __str__(self):
        return ("Reserva de "+self.nombre_huesped+" ("+ str(self.fecha_check_in)+"-"+str(self.fecha_check_out)+")")

# Check in
class FichaIngreso(models.Model):
    TIPODOC = (('DNI','DNI'),
              ('Pasaporte','Pasaporte'),)
    reserva = models.ForeignKey('Reserva', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50, verbose_name='Nombre del huésped')
    apellido = models.CharField(max_length=50, verbose_name='Apellido del huésped')
    tipo_documento = models.CharField(max_length=10, choices=TIPODOC, verbose_name='Tipo de documento')
    numero_documento = models.CharField(max_length=50, verbose_name='Número de documento')
    nacionalidad = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField(verbose_name='Fecha de nacimiento')
    domicilio = models.CharField(max_length=50, blank = True, null = True)
    foto_frente = models.ImageField(upload_to='documentacion/', null=True, blank=True)
    foto_reverso = models.ImageField(upload_to='documentacion/', null=True, blank=True)

class DJCovid(models.Model):
    ficha_ingreso = models.OneToOneField('FichaIngreso', on_delete=models.CASCADE, primary_key=True,)
    procedencia = models.CharField(max_length=50, blank = True, null = True)
    zona_riesgos = models.BooleanField(verbose_name='Zona de riesgo', default=False)
    sintomas = models.BooleanField(verbose_name='Síntomas', default=False)
    contacto_covid = models.BooleanField(verbose_name='Contacto con persona diagnóstico Covid', default=False)
    acudido_medico = models.BooleanField(verbose_name='Acudido al médico', default=False)
    sospecha = models.BooleanField(verbose_name='Sospecha', default=False)
    fecha_declaracion = models.DateField(verbose_name='Fecha de declaración', default=date.today()) #auto_now_add=True, 

class SolicitudIngresoRapido(models.Model):
    ESTADOS = (('Aceptado','Aceptado'),
              ('Rechazado','Rechazado'),
              ('Pendiente','Pendiente'),)
    reserva = models.OneToOneField('Reserva', on_delete=models.CASCADE, primary_key=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, verbose_name='Estado de solicitud', default='Pendiente')
    respuesta = models.CharField(max_length=50, verbose_name='Respuesta del alojamiento', blank = True, null = True)
    fecha_solicitud = models.DateField(verbose_name='Fecha de solicitud', auto_now_add=True)

# Notificaciones
class TipoNotificacion(models.Model):
    EMISOR = (('Infuetur','Infuetur'),
                ('Responsable','Responsable'))
    nombre = models.CharField(max_length=40)
    emisor = models.CharField(choices=EMISOR, max_length=40)

    def __str__(self):
        return (self.nombre)

class Notificacion(models.Model):
    tipo_notificacion = models.ForeignKey('TipoNotificacion', on_delete=models.CASCADE)
    reserva = models.ForeignKey('Reserva', null=True, blank=True, on_delete=models.CASCADE)
    alojamiento = models.ForeignKey('Alojamiento', null=True, blank=True, on_delete=models.CASCADE)
    # null True para que una notificación no necesite estar vinculada a una reserva en particular
    titulo = models.CharField(max_length=40)
    descripcion = models.CharField(max_length=150)
    fecha = models.DateField(verbose_name='Fecha de solicitud', auto_now_add=True)
    visto = models.BooleanField(verbose_name='Visto', default=False)

# Desayuno
class PedidoDesayuno(models.Model):
    reserva = models.ForeignKey('Reserva', on_delete=models.CASCADE)
    fechaDesayuno = models.DateField(verbose_name='Fecha de desayuno', default=date.today)#auto_now_add=True)
    horaDesayuno = models.TimeField(verbose_name='Hora de desayuno')
    takeaway = models.BooleanField(verbose_name='Take away', default=False)
    comentario = models.CharField(max_length=150, null=True, blank=True)

class ItemPedido(models.Model):
    pedidoDesayuno = models.ForeignKey('PedidoDesayuno', on_delete=models.CASCADE)
    #itemDesayuno = models.ForeignKey('ItemDesayuno', null=True, on_delete=models.SET_NULL)
    configuracionDesayuno = models.ForeignKey('ConfiguracionDesayuno', null=True, on_delete=models.SET_NULL,verbose_name='Item')
    cantidad = models.IntegerField(verbose_name='Cantidad')

class ItemDesayuno(models.Model):
    CATEGORIAS = (('Bebidas calientes','Bebidas calientes'),
                ('Bebidas frias','Bebidas frias'),
                ('Panaderia/reposteria','Panaderia/reposteria'),
                ('Cereales/Semillas','Cereales/semillas'),
                ('Fiambres/lacteos','Fiambres/lacteos'),
                ('Frutas/verduras','Frutas/verduras'),
                ('Mermeladas/dulces','Mermeladas/dulces'),
                ('Aderezos','Aderezos'),
                ('Endulzante','Endulzante'),)
    UNIDADES = (('Taza','Taza'),
                ('Vaso','Vaso'),
                ('Unidad','Unidad'),
                ('Feta','Feta'),
                ('Cuchara','Cuchara'),
                ('Cucharita','Cucharita'),)
    nombre = models.CharField(max_length=30)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    unidad = models.CharField(max_length=10, choices=UNIDADES, default='Unidad')
    def __str__(self):
        return (self.nombre)

class ConfiguracionDesayuno(models.Model):
    alojamiento = models.ForeignKey('Alojamiento', on_delete=models.CASCADE)
    itemDesayuno = models.ForeignKey('ItemDesayuno', null=True, on_delete=models.SET_NULL)
#    cantidadMaxima = models.IntegerField(verbose_name='Cantidad máxima por huésped')# Cantidad máxima que puede pedir un huésped de ese item por desayuno
    def __str__(self):
#        return (self.itemDesayuno.nombre+' ('+self.itemDesayuno.unidad+')')
        return (self.itemDesayuno.nombre)

# Contenido
# Faltan definir dos clases de contenido de servicios del alojamiento