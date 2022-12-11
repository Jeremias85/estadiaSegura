from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, User
from estadiatdf.models import TipoNotificacion

class Command(BaseCommand):
    help = 'Carga Inicial'

    def handle(self, *args, **options):
        try:
            admin_infuetur = Group(name='AdminINFUETUR')
            admin_infuetur.save()
            responsable = Group(name='Responsable')
            responsable.save()
            notificacion_sir = TipoNotificacion(nombre='Ingreso Rápido', emisor='Responsable')
            notificacion_sir.save()
            estadiatdf = User.objects.create_user(username='estadiatdf', email='estadiatdf@test.com', password='Laboratorio2020')
            estadiatdf.save()
            admin_infuetur.user_set.add(estadiatdf)
            self.stdout.write(self.style.SUCCESS('Carga inicial completa.'))
        except:
            self.stdout.write(self.style.SUCCESS('Error en la carga inicial.'))