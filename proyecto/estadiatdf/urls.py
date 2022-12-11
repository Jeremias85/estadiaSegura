#from proyecto.estadiatdf.views import huesped_views
from django.conf.urls import url, include
from django.urls import path
from django.contrib.auth.urls import urlpatterns,path
from django.contrib.auth.models import User

from . import views
from .views import Bienvenida, CrearFichaIngreso, InicioAdministracion, ListaAlojamientos, FichaAlojamiento, PedidoDesayunoEncargadoDetailView
from .views import ListaNotificacionesINFUETUR, NotificacionInfueturCreate, FichaNotificacionInfuetur
from .views import PruebaI18n, ReservaCreate, ListaReservas, FichaReserva, ReservaUpdate, ConfigurarDesayuno, ListaPedidosDesayuno, ListaNotificacionesRecibidasResponsable, ListaNotificacionesEnviadasResponsable,FichaNotificacionResponsable,NotificacionResponsableCreate
from .views import HomeReserva, WebCheckIn
from .views import CrearFichaIngreso, CrearDJCovid, VerFichaIngreso, VerDJCovid, ModificarFichaIngreso, ModificarDJCovid
from .views import SolicitarIngresoRapido, ListaNotificaciones, FichaNotificacion, TarjetaIngresoRapido
from .views import huesped_views, MiDesayuno, VerPedidoDesayuno, ModificarPedidoDesayuno, Unauthorized
#from .views.huesped_views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [


    url(r'^$', Bienvenida.as_view(), name='bienvenida'),

    url(r'^unauthorized/$', Unauthorized.as_view(), name='unauthorized'),

    # Administración INFUETUR/Encargado de alojamiento
    url(r'^administracion/$', InicioAdministracion.as_view(), name='inicio'),

    # Encargado de alojamiento
    url(r'^administracion/reservas/crear/$', ReservaCreate.as_view(), name='crearReserva'),
    url(r'^administracion/reservas/$', ListaReservas.as_view(), name='listaReservas'),
    url(r'^administracion/reservas/(?P<pk>\d+)$', FichaReserva.as_view(), name='fichaReserva'),
    url(r'^administracion/reservas/modificar/(?P<pk>\d+)$', ReservaUpdate.as_view(), name='modificarReserva'),
    url(r'^administracion/desayuno/configurar/$', ConfigurarDesayuno.as_view(), name="configurarDesayuno"),
    url(r'^administracion/desayuno/pedidos/$', ListaPedidosDesayuno.as_view(), name='listaPedidosDesayuno'),
    url(r'^administracion/desayuno/pedido/(?P<pk>\d+)$', PedidoDesayunoEncargadoDetailView.as_view(), name='detallePedidoEncargado'),
    url(r'^administracion/notificacion/recibidas/$', ListaNotificacionesRecibidasResponsable.as_view(), name='listaNotificacionesRecibidasResponsable'),
    url(r'^administracion/notificacion/enviadas/$', ListaNotificacionesEnviadasResponsable.as_view(), name='listaNotificacionesEnviadasResponsable'),
    url(r'^administracion/encargado/notificaciones/(?P<pk>\d+)$', FichaNotificacionResponsable.as_view(), name='fichaNotificacionResponsable'),
    url(r'^administracion/notificaciones/encargado/crear/$', NotificacionResponsableCreate.as_view(), name='nuevaNotificacionResponsable'),

    # Prueba i18n
    #url(r'^prueba/(?P<m>\d+)$', views.my_view, name='my_view'),
    url(r'^i18n/$', PruebaI18n.as_view(), name='i18n'),

    # INFUETUR
    url(r'^administracion/alojamientos/$', ListaAlojamientos.as_view(), name='listaAlojamientos'),
    url(r'^administracion/alojamientos/(?P<pk>\d+)$', FichaAlojamiento.as_view(), name='fichaAlojamiento'),
    url(r'^administracion/notificaciones/$', ListaNotificacionesINFUETUR.as_view(), name='listaNotificacionesINFUETUR'),
    url(r'^administracion/notificaciones/crear/$', NotificacionInfueturCreate.as_view(), name='nuevaNotificacionINFUETUR'),
    url(r'^administracion/notificaciones/(?P<pk>\d+)$', FichaNotificacionInfuetur.as_view(), name='fichaNotificacionINFUETUR'),

    # Huésped
    url(r'^reserva/$', HomeReserva.as_view(), name='homeReserva'),
    
    url(r'^reserva/check-in/$', WebCheckIn.as_view(), name='webCheckIn'),
    url(r'^reserva/crearFichaIngreso/$', CrearFichaIngreso.as_view(), name='crearFicha'),
    url(r'^reserva/crearDJCovid/$', CrearDJCovid.as_view(), name='crearDJCovid'),
    url(r'^reserva/verFichaIngreso/(?P<pk>\d+)$', VerFichaIngreso.as_view(), name='verFichaIngreso'),
    url(r'^reserva/verDJCovid/(?P<pk>\d+)$', VerDJCovid.as_view(), name='verDJCovid'),
    url(r'^reserva/modificarFichaIngreso/(?P<pk>\d+)$', ModificarFichaIngreso.as_view(), name='modificarFichaIngreso'),
    url(r'^reserva/modificarDJCovid/(?P<pk>\d+)$', ModificarDJCovid.as_view(), name='modificarDJCovid'),

    url(r'^reserva/solicitarIR/(?P<pk>\d+)$', SolicitarIngresoRapido.as_view(), name='solicitarIR'),
    url(r'^reserva/tarjetaIngreso/$', TarjetaIngresoRapido.as_view(), name='tarjetaIngreso'),
    
    url(r'^reserva/notificaciones/$', ListaNotificaciones.as_view(), name='listaNotificaciones'),
    url(r'^reserva/notificacion/(?P<pk>\d+)$', FichaNotificacion.as_view(), name='fichaNotificacion'),
    
    url(r'^reserva/miDesayuno/$', MiDesayuno.as_view(), name='miDesayuno'),
    url(r'^reserva/pedidoDesayuno/$', huesped_views.create_book_with_authors, name='pedidoDesayuno'),
    url(r'^reserva/verPedidoDesayuno/(?P<pk>\d+)$', VerPedidoDesayuno.as_view(), name='verPedidoDesayuno'),
    url(r'^reserva/modificarPedidoDesayuno/(?P<pk>\d+)$', ModificarPedidoDesayuno.as_view(), name='modificarPedidoDesayuno'),

    # Cuentas
    path('accounts/', include('django.contrib.auth.urls')),

    # Prueba cookies
    path('test_cookie/', views.test_cookie, name='test_cookie'),

    url(r'^signup/$', views.signup, name='signup'),

    ]

# Carga los media en el ámbito de producción
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
