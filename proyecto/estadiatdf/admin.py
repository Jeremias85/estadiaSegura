from django.contrib import admin
from .models import Alojamiento, Contacto, FichaIngreso, DJCovid, Reserva, SolicitudIngresoRapido
from .models import Notificacion, TipoNotificacion, PedidoDesayuno, ItemDesayuno, ItemPedido, ConfiguracionDesayuno
# Register your models here.

admin.site.register(Alojamiento)
admin.site.register(Contacto)
admin.site.register(Reserva)
admin.site.register(FichaIngreso)
admin.site.register(DJCovid)
admin.site.register(SolicitudIngresoRapido)
admin.site.register(TipoNotificacion)
admin.site.register(Notificacion)
admin.site.register(PedidoDesayuno)
admin.site.register(ItemDesayuno)
admin.site.register(ItemPedido)
admin.site.register(ConfiguracionDesayuno)

