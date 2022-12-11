from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.models import User, Group
from ..models import Alojamiento, ConfiguracionDesayuno, Contacto, DJCovid, FichaIngreso, Notificacion, Reserva, SolicitudIngresoRapido
from ..models import ItemPedido, PedidoDesayuno, ItemDesayuno
from django.http import HttpResponse, HttpResponseNotFound
from ..forms import ReservaForm, FichaIngresoForm, DJCovidForm, ItemPedidoFormset, PedidoDesayunoModelForm
from ..forms import SignUpForm, EmailTokenForm
from django.utils.translation import gettext
from datetime import date, time, datetime, timedelta
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import FormMixin
from django.urls import reverse
from django.core.mail import send_mail
import uuid
from ..constant import *
from django.db.models import Q

# Prueba de Internacionalización
class PruebaI18n(TemplateView):
    template_name = "huesped/i18n.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

# Prueba de uso de cookies
def test_cookie(request):   
    if not request.COOKIES.get('team'):
        response = HttpResponse("Visiting for the first time.")
        response.set_cookie('team', 'barcelona')
        return response
    else:
        return HttpResponse("Your favorite team is {}".format(request.COOKIES['team']))

    # RECORDAR DE MODIFICAR EL TIEMPO DE LA COOKIE, POR AHORA SÓLO ESTÁ DURANDO LO QUE DURA LA SESIÓN DEL
    # BROWSER (CUANDO SE CIERRA SE BORRA LA COOKIE)
    # set_cookie(key, value='', max_age=None, expires=None, path='/', 
    # domain=None, secure=None, httponly=False, samesite=None)
    # max_age = 365 * 24 * 60 * 60  # one year
    
    # Enviar por email invitación al huésped (con el token)
    # http://127.0.0.1:8000/reserva/?token=34fdg455
    # http://127.0.0.1:8000/reserva/?token=3cf8ca5d-de2f-4962-85e8-11b9f20e8cbb
    # Habría que recibir los parámetros de la url con el token de la invitación
    # La primera vez que se accede con la url de la invitación, set_cookie['token'] = valorToken
    # La segunda vez habría que verificar el valorToken guardado en la cookie de la computadora contra el 
    # token guardado en el servidor para saber de que reserva estamos hablando
    # Y si tiene más de una reserva? Sería mejor un par (key,value) = (numeroReserva, tokenReserva)

class HomeReserva(TemplateView):
    template_name = "huesped/home_reserva.html"

    def render_to_response(self, context, **response_kwargs):
        response = super(HomeReserva, self).render_to_response(context, **response_kwargs)

        # Se obtiene token del URL
        tokenURL = self.request.GET.get('token')
        if tokenURL:
            response.set_cookie('token', tokenURL)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Se obtiene el token del huésped
        tokenURL = self.request.GET.get('token')
        
        if tokenURL or self.request.COOKIES.get('token'):
            try:
                if tokenURL:
                    reserva = Reserva.objects.get(token=str(tokenURL))
                else:
                    reserva = Reserva.objects.get(token=str(self.request.COOKIES.get('token')))
                context ['reserva'] = reserva

                # Hay que mostrar las notificaciones que envian del establecimiento y las del INFUETUR
                """try:
                    notificacionesVistas = self.request.session['vistos']
                except:
                    self.request.session['vistos'] = {}

                notificacionesVistas['5'] = '5'
                self.request.session['vistos'] = notificacionesVistas
                notificacionesVistas = self.request.session['vistos']

                notificacionesInfuetur = Notificacion.objects.filter(tipo_notificacion__emisor='Infuetur')
                """
                #self.request.session['notificacionesVistas'].add('5')
                """for key in notificacionesVistas:
                    total = total + notificacionesVistas[key]
                context['fechaNotificacion'] = total
                """
                fechaHoy = date.today()
                notificaciones = Notificacion.objects.filter(reserva=reserva).filter(visto=False).order_by('-fecha')
                #notificaciones = Notificacion.objects.filter(
                #    Q(reserva=reserva) | Q(fecha=fechaHoy)
                #    ).filter(visto=False).order_by('-fecha')

                #notificacionesInfuetur.union(notificaciones)
                #context['notificaciones'] = notificacionesInfuetur #notificaciones
                
                context['notificaciones'] = notificaciones

                #alojamiento = Alojamiento.objects.get(id=reserva.alojamiento_id)
                #context ['alojamiento'] = alojamiento
            except:
                pass
                
        return context

class WebCheckIn(TemplateView):
    template_name = "huesped/web_check_in.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        reserva = Reserva.objects.get(token=str(self.request.COOKIES.get('token')))
        context ['reserva'] = reserva
        
        # ingresoRapido significa que puede enviar esa solicitud
        ingresoRapido = False
        # SolicitudEnviada significa si existe la solicitud
        solicitudEnviada = False
        # solicitudAceptada significa que el encargado ha aceptado la solicitud de Ingreso Rápido
        solicitudAceptada = False

        fichas = FichaIngreso.objects.filter(reserva=reserva)
        context['fichas'] = fichas

        # Todavía faltan cargar fichas
        if fichas.count() < reserva.pax:
            nuevoIntegrante = True
            context['nuevoIntegrante'] = nuevoIntegrante

        ddjjcovid = DJCovid.objects.filter(ficha_ingreso__reserva=reserva)
        if ddjjcovid.count() == reserva.pax:
            try:
                solicitud = SolicitudIngresoRapido.objects.filter(reserva=reserva).last()
                if solicitud.estado == 'Rechazado':
                    ingresoRapido = True
                    solicitudEnviada = False
                else:
                    ingresoRapido = False
                    solicitudEnviada = True
                    if solicitud.estado == 'Aceptado':
                        solicitudAceptada = True
            except:
                ingresoRapido = True
        context['solicitudEnviada'] = solicitudEnviada
        context['ingresoRapido'] = ingresoRapido
        context['solicitudAceptada'] = solicitudAceptada

        return context

class CrearFichaIngreso(CreateView):
    template_name = "huesped/crear_ficha_ingreso.html"
    model = FichaIngreso
    form_class = FichaIngresoForm
    success_url = reverse_lazy('crearDJCovid')
    
    def form_valid(self, form):
        reserva = Reserva.objects.get(token=str(self.request.COOKIES.get('token')))
        form.instance.reserva = reserva
        form.instance.save()
        self.request.session['ficha_id'] = form.instance.id
        return super().form_valid(form)

class CrearDJCovid(CreateView):
    template_name = "huesped/crear_dj_covid.html"
    model = DJCovid
    form_class = DJCovidForm
    success_url = reverse_lazy('webCheckIn')

    def form_valid(self, form):
        reserva = Reserva.objects.get(token=str(self.request.COOKIES.get('token')))
        fichaIngreso = FichaIngreso.objects.get(id=self.request.session['ficha_id']) 
        self.request.session['ficha_id'] = {} # Lo borro para que no tenga un valor basura para la próxima
        form.instance.ficha_ingreso = fichaIngreso
        form.instance.save()
        return super().form_valid(form)

class VerFichaIngreso(TemplateView):
    template_name = "huesped/ver_ficha_ingreso.html"

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        context = super().get_context_data(**kwargs)

        reserva = Reserva.objects.get(token=str(self.request.COOKIES.get('token')))
        try:
            ficha = FichaIngreso.objects.get(id=pk)
            if ficha.reserva == reserva:
                context['autorizado'] = True
                context['ficha'] = ficha
            else:
                context['autorizado'] = False
        except:
            context['autorizado'] = False

        try:
            declaracionCovid = DJCovid.objects.get(ficha_ingreso=ficha) 
            context['declaracionJurada'] = True
            context['declaracionJuradaId'] = ficha.id#declaracionCovid.id
        except:
            self.request.session['ficha_id'] = ficha.id
            context['declaracionJurada'] = False
        
        return context

class VerDJCovid(TemplateView):
    template_name = "huesped/ver_dj_covid.html"

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        context = super().get_context_data(**kwargs)

        reserva = Reserva.objects.get(token=str(self.request.COOKIES.get('token')))
        try:
            #ficha = FichaIngreso.objects.get(id=pk)
            declaracionCovid = DJCovid.objects.get(ficha_ingreso_id=pk)
            if declaracionCovid.ficha_ingreso.reserva == reserva: #if declaracionCovid.ficha_ingreso.reserva == reserva:
                context['autorizado'] = True
                context['declaracionJurada'] = declaracionCovid
            else:
                context['autorizado'] = False
        except:
            context['autorizado'] = False
            context['noEncuentraDJ'] = True

        return context

# Se puede modificar la ficha de ingreso y la declaración jurada Covid mientras no exista solicitud de Ingreso
# Rápido o si la solicitud fue rechazada
class ModificarFichaIngreso(UpdateView):
    template_name = "huesped/modificar_ficha_ingreso.html"
    model = FichaIngreso
    form_class = FichaIngresoForm

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        reserva = Reserva.objects.get(token=str(self.request.COOKIES.get('token')))

        try:
            solicitud = SolicitudIngresoRapido.objects.filter(reserva=reserva).last()
            if solicitud.estado == 'Rechazado':
                context['formularioModificable'] = True
            else:
                context['formularioModificable'] = False
        except:
            context['formularioModificable'] = True

        return context

    def get_success_url(self):
        return reverse_lazy('verFichaIngreso', kwargs={'pk': self.kwargs['pk']})

class ModificarDJCovid(UpdateView):
    template_name = "huesped/modificar_dj_covid.html"
    model = DJCovid
    form_class = DJCovidForm

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        reserva = Reserva.objects.get(token=str(self.request.COOKIES.get('token')))

        try:
            solicitud = SolicitudIngresoRapido.objects.filter(reserva=reserva).last()
            if solicitud.estado == 'Rechazado':
                context['formularioModificable'] = True
            else:
                context['formularioModificable'] = False
        except:
            context['formularioModificable'] = True

        return context

    def get_success_url(self):
        return reverse_lazy('verDJCovid', kwargs={'pk': self.kwargs['pk']})

# El huésped solicitaría el ingreso rápido y ahí se crearía una SOLICITUD con el número de la reserva
# del mismo, la fecha del momento, el estado no-visto y sin respuesta.
# Si se ha enviado una solicitud de ingreso rápido no se puede modificar la ficha de ingreso ni la dj Covid
# Cuando acepta o rechaza la solicitud el encargado del alojamiento mediante el formulario de carga,
# en ese momento se crea la NOTIFICACION que recibirá el huésped, con el campo extra, visto.
# En el home de la versión celular del huésped se filtran todas las notificaciones en que el campo visto 
# sea False y se las muestra en forma de Pop-up (Toast).
# Al presionar sobre "Ver notificación" se muestra la notificación completa, además de cambiar el estado de
# la variable visto a True (ya no se verá más el Toast de esta notificación)

class SolicitarIngresoRapido(TemplateView):
    template_name = "huesped/solicitar_ingreso_rapido.html"

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        
        reservaSolicitud = Reserva.objects.get(id=pk)
        try:
            # Consulta si existe la solicitud, en caso de existir setearlo a Pendiente
            solicitudExistente = SolicitudIngresoRapido.objects.get(reserva=reservaSolicitud)
            solicitudExistente.estado = 'Pendiente'
            solicitudExistente.save()
        except:
            # En el caso de no existir la solicitud, crearla
            solicitud = SolicitudIngresoRapido.objects.create(reserva=reservaSolicitud,estado='Pendiente')

        return context

class ListaNotificaciones(TemplateView):
    template_name = "huesped/lista_notificaciones.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            reserva = Reserva.objects.get(token=str(self.request.COOKIES.get('token')))
            context['reserva'] = reserva
        except:
            context['reserva'] = False
            return context

        try:
            notificaciones = Notificacion.objects.filter(reserva=reserva).order_by('-fecha')
            context['notificaciones'] = notificaciones
        except:
            context['reserva'] = False
            return context
        
        return context

class FichaNotificacion(TemplateView):
    template_name = "huesped/ficha_notificacion.html"

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        
        reserva = Reserva.objects.get(token=str(self.request.COOKIES.get('token')))
        context['reserva'] = reserva
        try:
            notificacion = Notificacion.objects.get(id=pk)
            context['notificacion'] = notificacion
            if (notificacion.tipo_notificacion.nombre == "Situación epidemiológica") or (notificacion.tipo_notificacion.nombre == "Protocolo COVID"):
                pass
            else:
                notificacion.visto = True
                notificacion.save()
        except:
            context['notificacion'] = False

        return context

class TarjetaIngresoRapido(TemplateView):
    template_name = "huesped/tarjeta_ingreso_rapido.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reserva = Reserva.objects.get(token=str(self.request.COOKIES.get('token')))
        try:
            # Sería más fácil solo verificar si en la reserva el campo ingreso rápido está en True
            solicitud = SolicitudIngresoRapido.objects.filter(reserva=reserva).last()
            context['reserva'] = reserva
        except:
            pass

        return context

    # Para el desayuno verificar que los días que puede hacer el pedido son el día de check-in hasta
    # el día de Check-out inclusive

class MiDesayuno(TemplateView):
    template_name = "huesped/mi_desayuno.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['pedirDesayuno'] = False
        
        try:
            reserva = Reserva.objects.get(token=str(self.request.COOKIES.get('token')))
            context['reserva'] = True
        except:
            context['reserva'] = False
            return context


        try:
            pedidoDesayuno = PedidoDesayuno.objects.filter(reserva=reserva)
            context['fichasDesayunos'] = pedidoDesayuno
        except:
            context['fichasDesayunos'] = False

        fechaActual = date.today()
        horaActual = datetime.now().time()#.replace(hour=8, minute=0, second=1)

        # Si no está incluida la fechaActual entre fecha_check_in y fecha_check_out entonces se pasó la reserva 
        # En cambio, si fecha check_in <= fechaActual <= fecha check_out

       
        if fechaActual >= reserva.fecha_check_in and fechaActual <= reserva.fecha_check_out:
            if horaActual >= HORACOMIENZOPEDIDO and horaActual <= HORAMEDIANOCHE24: #  Próximo día
                try:
                    pedidoDesayuno = PedidoDesayuno.objects.filter(reserva=reserva).get(fechaDesayuno=fechaActual+timedelta(days=+1))
                    context['pedirDesayuno'] = False
                except:
                    context['pedirDesayuno'] = True
            elif horaActual >= HORAMEDIANOCHE0 and horaActual <= HORAFINALIZA: # Mismo día
                try:
                    pedidoDesayuno = PedidoDesayuno.objects.filter(reserva=reserva).get(fechaDesayuno=fechaActual)
                    context['pedirDesayuno'] = False
                except:
                    context['pedirDesayuno'] = True
    
        return context

def puedePedirDesayuno(reserva):
    
    fechaActual = date.today()
    horaActual = datetime.now().time()#.replace(hour=20, minute=0, second=1)

    if fechaActual >= reserva.fecha_check_in and fechaActual <= reserva.fecha_check_out:
        if horaActual >= HORACOMIENZOPEDIDO and horaActual <= HORAMEDIANOCHE24: # Próximo día
            try:
                pedidoDesayuno = PedidoDesayuno.objects.filter(reserva=reserva).get(fechaDesayuno=fechaActual+timedelta(days=+1))
                return False
            except:
                return True
        elif horaActual >= HORAMEDIANOCHE0 and horaActual <= HORAFINALIZA: # Mismo día
            try:
                pedidoDesayuno = PedidoDesayuno.objects.filter(reserva=reserva).get(fechaDesayuno=fechaActual)
                return False
            except:
                return True
        else:
            return False
    else:
        return False
    
# Pedido de desayuno
def create_book_with_authors(request):
    template_name = 'huesped/crearPedido.html'

    try:
        reserva = Reserva.objects.get(token=str(request.COOKIES.get('token')))
        if puedePedirDesayuno(reserva):
            
            fechaActual = date.today()
            horaActual = datetime.now().time()#.replace(hour=20, minute=0, second=1)
        
            if horaActual >= HORACOMIENZOPEDIDO and horaActual <= HORAMEDIANOCHE24 :
                fechaPedido = date.today() + timedelta(days=+1) 
            else:
                fechaPedido = date.today()

            if request.method == 'GET':
                pedidoDesayunoForm = PedidoDesayunoModelForm(request.GET or None)
                formset = ItemPedidoFormset(queryset=ItemPedido.objects.none())
                for form in formset:
                    form.fields['configuracionDesayuno'].queryset = ConfiguracionDesayuno.objects.filter(alojamiento=reserva.alojamiento)
            elif request.method == 'POST':
                pedidoDesayunoForm = PedidoDesayunoModelForm(request.POST)
                formset = ItemPedidoFormset(request.POST)
                if pedidoDesayunoForm.is_valid() and formset.is_valid():
                    pedidoDesayuno = pedidoDesayunoForm.save(commit=False)
                    pedidoDesayuno.reserva = reserva
                    pedidoDesayuno.fechaDesayuno = fechaPedido
                    pedidoDesayuno.save()
                    for form in formset:
                        if form.instance.cantidad == None:
                            pass
                        else:
                            itemPedido = form.save(commit=False)
                            itemPedido.pedidoDesayuno = pedidoDesayuno
                            itemPedido.save()
                    return redirect('miDesayuno')
            return render(request, template_name, {
                'bookform': pedidoDesayunoForm,
                'formset': formset,
                'reserva': reserva,
                'fechaPedido': fechaPedido,
            })
        else:
            pass
    except:
        pass
    return render(request, template_name, {
        'reserva': False,
    })

class VerPedidoDesayuno (TemplateView):
    template_name = "huesped/ver_pedido_desayuno.html"
    
    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        
        try:
            reserva = Reserva.objects.get(token=str(self.request.COOKIES.get('token')))
            context['reserva'] = True
        except:
            context['reserva'] = False
            return context
        
        try:
            pedido = PedidoDesayuno.objects.get(reserva=reserva,id=pk)
            context['pedido'] = pedido
        except:
            context['pedido'] = False
            return context

        try:
            ItemsPedido = ItemPedido.objects.filter(pedidoDesayuno=pedido)
            context['ItemsPedido'] = ItemsPedido
        except:
            pass

        fechaPedido = pedido.fechaDesayuno
        fechaActual = date.today()
        horaActual = datetime.now().time()#.replace(hour=8, minute=0, second=1)

        if fechaActual == fechaPedido - timedelta(days=+1):
            if horaActual < HORACOMIENZOPEDIDO:
                context['modificable'] = False
            else:
                context['modificable'] = True
        elif fechaActual == fechaPedido:
            if horaActual > HORAFINALIZA:
                context['modificable'] = False
            else:
                context['modificable'] = True

        return context

class ModificarPedidoDesayuno(UpdateView):
    template_name = "huesped/modificar_pedido_desayuno.html"
    model = PedidoDesayuno
    form_class = PedidoDesayunoModelForm

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        reserva = Reserva.objects.get(token=str(self.request.COOKIES.get('token')))
        pedido = PedidoDesayuno.objects.get(id=pk)
        context['fechaPedido'] = pedido.fechaDesayuno

        fechaPedido = pedido.fechaDesayuno
        fechaActual = date.today()
        horaActual = datetime.now().time()#.replace(hour=8, minute=0, second=1)

        if fechaActual == fechaPedido - timedelta(days=+1):
            if horaActual < HORACOMIENZOPEDIDO:
                context['modificable'] = False
            else:
                context['modificable'] = True
        elif fechaActual == fechaPedido:
            if horaActual > HORAFINALIZA:
                context['modificable'] = False
            else:
                context['modificable'] = True

        qs = ItemPedido.objects.filter(pedidoDesayuno=self.get_object())
        formset = ItemPedidoFormset(queryset=qs)
        context['formset'] = formset
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        qs = ItemPedido.objects.filter(pedidoDesayuno=self.get_object())
        formsets = ItemPedidoFormset(self.request.POST, queryset=qs)
        pk = self.kwargs['pk']
        pedido = PedidoDesayuno.objects.get(id=pk)
        if form.is_valid():
            for fs in formsets:
                if fs.is_valid():
                    if fs.instance.cantidad == None:
                        pass
                    else:
                        itemPedido = fs.save(commit=False)
                        itemPedido.pedidoDesayuno = pedido
                        itemPedido.save()
            # No está capturando cuando no se coloca nada en la cantidad, no 0, NONE
            if formsets.is_valid:
                instances = formsets.save(commit=False)
                for obj in formsets.deleted_objects:
                    try:
                        obj.delete()
                    except:
                        pass
            return self.form_valid(form)
        return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('verPedidoDesayuno', kwargs={'pk': self.kwargs['pk']})
