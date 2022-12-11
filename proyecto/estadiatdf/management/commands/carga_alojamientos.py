from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from requests.exceptions import ConnectionError
from estadiatdf.models import Alojamiento, Contacto
from django.db import connection
import requests

class Command(BaseCommand):
    help = 'Carga y actualización de alojamientos'

    def add_arguments(self, parser):
        parser.add_argument('user', type=str, help='Usuario SUIT')
        parser.add_argument('password', type=str, help='Contrasena del usuario SUIT')

    def handle(self, *args, **kwargs):        
        try:
            user = kwargs['user']
            password = kwargs['password']
            url = 'https://suit.tur.ar/api/1.1.0/alojamientos/'
            response = requests.get(url, auth=(user, password))
            data = response.json()
            alojamientos = data
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM estadiatdf_contacto")
                cursor.execute("DELETE FROM SQLite_sequence WHERE name='estadiatdf_contacto'")
            for i in alojamientos:
                if "foto" in i:
                    i_url = i['foto']
                else:
                    i_url = None
                try:            
                    alojamiento_data  = Alojamiento.objects.get(suit_id=i['id'])
                    alojamiento_data.nombre = i['nombre']
                    alojamiento_data.domicilio = i['domicilio']
                    alojamiento_data.localidad = i['localidad']['nombre']
                    alojamiento_data.cuit = i['cuit']
                    alojamiento_data.image_url = i_url
                    contactos = i['contactos']
                    for j in contactos:
                        contacto_data = Contacto(
                            tipo = j['tipo'],
                            valor = j['valor'],
                            alojamiento = alojamiento_data,
                        )
                        contacto_data.save()
                    self.stdout.write(self.style.SUCCESS('Alojamiento "%s (%s)" actualizado con exito!' % (alojamiento_data.nombre, alojamiento_data.suit_id)))  
                except ObjectDoesNotExist:
                    alojamiento_data = Alojamiento(
                        suit_id = i['id'],
                        nombre = i['nombre'],
                        domicilio = i['domicilio'],
                        localidad = i['localidad']['nombre'],
                        cuit = i['cuit'],
                        image_url = i_url,
                    )
                    alojamiento_data.save()
                    contactos = i['contactos']
                    for j in contactos:
                        contacto_data = Contacto(
                            tipo = j['tipo'],
                            valor = j['valor'],
                            alojamiento = alojamiento_data,
                        )
                        contacto_data.save()
                    self.stdout.write(self.style.SUCCESS('Alojamiento "%s (%s)" cargado con exito!' % (alojamiento_data.nombre, alojamiento_data.suit_id)))
        except ConnectionError:
            self.stdout.write(self.style.WARNING('Error de conexión. Enviando correo.'))
        except:
            self.stdout.write(self.style.WARNING('Error de en la carga de alojamientos.'))