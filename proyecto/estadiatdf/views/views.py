from asyncio.windows_events import NULL
from re import T
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.contrib.auth.models import User, Group
from ..models import Alojamiento, ConfiguracionDesayuno, FichaIngreso, ItemDesayuno, ItemPedido, PedidoDesayuno, Reserva, Notificacion, SolicitudIngresoRapido, TipoNotificacion
# from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.http import HttpResponseNotFound, HttpResponseRedirect
from ..forms import ReservaForm, SirEncargadoForm, EmailTokenForm, SignUpForm, ItemConfigurarDesayunoFormset, NotificacionResponsableForm
# from django.utils.translation import gettext
from datetime import date
from django.db.models import Q
from django.urls import reverse

from braces.views import GroupRequiredMixin
from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from django.core.mail import send_mail


#def my_view(request, m):
#    output = gettext('Hoy es %(month)s.') % {'month': m}
#    return HttpResponse(output)

class Bienvenida(TemplateView):
    template_name = "bienvenida/bienvenida.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

    #return context

class LoginView(TemplateView):
    template_name = "login.html"
    success_url = reverse_lazy('index')

class InicioAdministracion(TemplateView):
    template_name = "infuetur/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            idSesion = self.request.session['_auth_user_id']
            us = User.objects.get(id=idSesion)
            grupo = Group.objects.get(user__id=idSesion)
        except:
            # Si se trata de acceder al sistema pero no se ha logueado entonces directamente el controlador 
            # no envía nada a la vista
            return context

        # Si el usuario es admin del infuetur envía los datos de los alojamientos registrados y notificaciones
        if grupo.name == 'AdminINFUETUR':
            context['alojamientos'] = Alojamiento.objects.all
            context['notificaciones'] = Notificacion.objects.filter(tipo_notificacion__emisor='Infuetur')
        else:
            # Si el usuario es responsable de un alojamiento envía los datos de las reservas
            try:
                alojamientoDelResponsable = Alojamiento.objects.get(responsable=idSesion)
                context ['alojamientoResponsable'] = alojamientoDelResponsable
                # Se guarda en una variable de sesión el nombre del alojamiento del responsable
                self.request.session['alojamiento'] = str(alojamientoDelResponsable)

                # RECORDAR que puede no haber reservas, ver de poner otro try-catch
                context ['reservas'] = Reserva.objects.filter(alojamiento=alojamientoDelResponsable)
                hoy = date.today()
                context ['reservasHoy'] = Reserva.objects.filter(alojamiento=alojamientoDelResponsable).filter(fecha_check_in=hoy)
                context ['solicitudesPendientes'] = Reserva.objects.filter(alojamiento=alojamientoDelResponsable).filter(solicitudingresorapido__estado="Pendiente")
                #recordar que puede no haber reservas, ver de poner otro try-catch
            except:
                # Si el usuario tiene cuenta de responsable pero no tiene asignado ningún alojamiento
                context ['alojamientoResponsable'] = False 
        # Si el usuario es responsable de un alojamiento
        return context

class ReservaCreate(GroupRequiredMixin, CreateView):
    template_name = "encargado/reserva_form.html"
    model = Reserva
    form_class = ReservaForm
    success_url = reverse_lazy('listaReservas')
    group_required = u"Responsable"

    def form_valid(self, form):
        idSesion = self.request.session['_auth_user_id']
        alojamiento = Alojamiento.objects.get(responsable=idSesion)
        form.instance.alojamiento = alojamiento
        form.instance.save()
        return super().form_valid(form)

class ListaReservas(GroupRequiredMixin, TemplateView):
    template_name = "encargado/lista_reservas.html"
    group_required = u"Responsable"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            idSesion = self.request.session['_auth_user_id']
            alojamientoDelResponsable = Alojamiento.objects.get(responsable=idSesion)
            context['reservas'] = Reserva.objects.filter(alojamiento=alojamientoDelResponsable)
        except:
            context['reservas'] = {}
        return context

class FichaReserva(GroupRequiredMixin, TemplateView):
    template_name = "encargado/ficha_reserva.html"
    group_required = u"Responsable"

    def dispatch(self, *args, **kwargs):
        pk = self.kwargs['pk']
        try:
            idSesion = self.request.session['_auth_user_id']
            alojamientoDelResponsable = Alojamiento.objects.get(responsable=idSesion)
            reserva_data = Reserva.objects.filter(alojamiento=alojamientoDelResponsable).get(id=pk)
            return super(FichaReserva, self).dispatch(*args, **kwargs)
        except:
            return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        reserva_data = Reserva.objects.get(id=pk)
        context['reserva'] = reserva_data
        context['fichasIngreso'] = FichaIngreso.objects.filter(reserva=reserva_data)
        form = EmailTokenForm(self.request.POST or None)
        context['form'] = form
        try:
            sir = SolicitudIngresoRapido.objects.get(reserva=reserva_data)
            form_sir = SirEncargadoForm(self.request.POST or None, instance=sir)
            context['form_sir'] = form_sir
        except:
            pass
        context['pk'] = pk
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        pk = context['pk']
        if request.method=='POST' and 'enviarEmail' in request.POST:
            form = context['form']
            if form.is_valid():
                reserva = Reserva.objects.get(id=pk)
                subject = "Invitacion Estadia Segura"
                message = "Para gestionar su reserva ingrese al siguiente link: " + "http://127.0.0.1:8000/reserva/?token=" + str(reserva.token)
                from_email = "registro@estadiasegura.tur.ar"
                recipient_list = [form.cleaned_data['email']]
                try:
                    send_mail(subject, message, from_email, recipient_list)
                except:
                    pass
                return HttpResponseRedirect(reverse('fichaReserva', kwargs={'pk': pk}))
        if request.method=='POST' and 'modificarSolicitud' in request.POST:
            form_sir = context['form_sir']
            if form_sir.is_valid():
                # Modifico reserva
                reserva = form_sir.cleaned_data['reserva']
                estado = form_sir.cleaned_data['estado']
                respuesta = form_sir.cleaned_data['respuesta']
                sir_act = SolicitudIngresoRapido.objects.get(reserva = reserva)
                sir_act.estado = estado
                sir_act.respuesta = respuesta
                sir_act.save()
                # Genero notificación
                tnotificacion = TipoNotificacion.objects.get(nombre='Ingreso Rápido')
                if estado == 'Aceptado':
                    titulo_noti = 'Ingreso Rápido Aceptado'
                elif estado == 'Rechazado':
                    titulo_noti = 'Ingreso Rápido Rechazado'
                else:
                    titulo_noti = 'Ingreso Rápido Pendiente'
                if respuesta is None:
                    respuesta = 'Sin comentarios'
                n = Notificacion(tipo_notificacion=tnotificacion, reserva=reserva, titulo=titulo_noti, descripcion=respuesta)
                n.save()
                return HttpResponseRedirect(reverse('fichaReserva', kwargs={'pk': pk}))
        return super(TemplateView, self).render_to_response(context)

class ReservaUpdate(GroupRequiredMixin, UpdateView):
    template_name = "encargado/reserva_update_form.html"
    model = Reserva
    form_class = ReservaForm
    group_required = u"Responsable"

    def get_success_url(self):
        return reverse_lazy('fichaReserva', kwargs={'pk': self.kwargs['pk']})

    def dispatch(self, *args, **kwargs):
        pk = self.kwargs['pk']
        try:
            idSesion = self.request.session['_auth_user_id']
            alojamientoDelResponsable = Alojamiento.objects.get(responsable=idSesion)
            reserva_data = Reserva.objects.filter(alojamiento=alojamientoDelResponsable).get(id=pk)
            return super(ReservaUpdate, self).dispatch(*args, **kwargs)
        except:
            return redirect('unauthorized')

    def form_valid(self, form):
        pk = self.kwargs['pk']
        cant_pax_anterior = (Reserva.objects.get(id=pk)).pax
        cant_pax_actual = form.cleaned_data['pax']
        if cant_pax_anterior != cant_pax_actual:
            try:
                sir = SolicitudIngresoRapido.objects.get(reserva_id=pk)
                sir.delete()
            except:
                pass
            FichaIngreso.objects.filter(reserva__id=pk).delete()
        return super().form_valid(form)

def signup(request):
    uuid = request.GET['uuid']
    try:
        alojamiento = Alojamiento.objects.get(token=uuid)
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save()
                user.refresh_from_db()  # load the profile instance created by the signal
                user.first_name = form.cleaned_data.get('nombre')
                user.last_name = form.cleaned_data.get('apellido')

                miGrupo = Group.objects.get(name='Responsable')
                miGrupo.user_set.add(user)

                user.save()

                alojamiento.responsable = user # Si el formulario es valido cargo el usuario al alojamiento
                alojamiento.token = None # Elimino el token utilizado
                alojamiento.save()

                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')

                user = authenticate(username=username, password=raw_password)
                login(request, user)
                return redirect('bienvenida')
        else:
            form = SignUpForm()
        return render(request, 'registration/signup.html', {'form': form})
    except ObjectDoesNotExist:
        return HttpResponseNotFound('<h1>Página no encontrada</h1>')

class Unauthorized(TemplateView):
    template_name = "general/unauthorized.html"

class ConfigurarDesayuno(GroupRequiredMixin, TemplateView):
    template_name = "encargado/configurar_desayuno.html"
    group_required = u"Responsable"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        idSesion = self.request.session['_auth_user_id']
        alojamientoDelResponsable = Alojamiento.objects.get(responsable=idSesion)
        itemsPrecargados = ConfiguracionDesayuno.objects.filter(alojamiento=alojamientoDelResponsable).order_by('itemDesayuno__nombre')
        formSetItems = []
        itemsPrecargadosLista = []
        for itemPre in itemsPrecargados:
            formSetItems.append({'nombre': itemPre.itemDesayuno.nombre, 'activo': True})
            itemsPrecargadosLista.append(itemPre.itemDesayuno.id)
        allItems = ItemDesayuno.objects.exclude(id__in=itemsPrecargadosLista).order_by('nombre')
        for item in allItems:
            formSetItems.append({'nombre': item.nombre, 'activo': False})
        formset = ItemConfigurarDesayunoFormset(initial= formSetItems)
        context['formset'] = formset
        return context
    
    def post(self, request, *args, **kwargs):
        items_formset = ItemConfigurarDesayunoFormset(request.POST)
        idSesion = self.request.session['_auth_user_id']
        alojamientoDelResponsable = Alojamiento.objects.get(responsable=idSesion)
        if items_formset.is_valid():
            for f in items_formset[:-1]:
                try:
                    activa = f.cleaned_data['activo']
                    nombre_item = f.cleaned_data['nombre']
                    if activa:
                        try:
                            itemConDe = ConfiguracionDesayuno.objects.filter(alojamiento= alojamientoDelResponsable).get(itemDesayuno__nombre= nombre_item)
                        except:
                            item = ItemDesayuno.objects.get(nombre= nombre_item)
                            itemConfiguracionDesayuno = ConfiguracionDesayuno(alojamiento= alojamientoDelResponsable, itemDesayuno= item)
                            itemConfiguracionDesayuno.save()
                    else:
                        try:
                            itemConDe = ConfiguracionDesayuno.objects.filter(alojamiento= alojamientoDelResponsable).get(itemDesayuno__nombre= nombre_item)
                            itemConDe.delete()
                        except:
                            pass
                except:
                    pass
        return HttpResponseRedirect(self.request.path_info)

    def get_success_url(self):
        return reverse_lazy('inicio')

class ListaPedidosDesayuno(GroupRequiredMixin, TemplateView):
    template_name = "encargado/lista_pedidos_desayuno.html"
    group_required = u"Responsable"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        idSesion = self.request.session['_auth_user_id']
        alojamientoDelResponsable = Alojamiento.objects.get(responsable=idSesion)
        reservas = Reserva.objects.filter(alojamiento=alojamientoDelResponsable)
        context['pedidos'] = PedidoDesayuno.objects.filter(reserva__in=reservas)
        return context

class PedidoDesayunoEncargadoDetailView(GroupRequiredMixin, TemplateView):
    PedidoDesayuno = PedidoDesayuno
    template_name = 'encargado/detalle_pedido_encargado.html'
    group_required = u"Responsable"

    def dispatch(self, *args, **kwargs):
        pk = self.kwargs['pk']
        try:
            idSesion = self.request.session['_auth_user_id']
            alojamientoDelResponsable = Alojamiento.objects.get(responsable=idSesion)
            pedido_desayuno = PedidoDesayuno.objects.get(id=pk)
            reserva_id = pedido_desayuno.reserva.id
            reserva_data = Reserva.objects.filter(alojamiento=alojamientoDelResponsable).get(id=reserva_id)
            return super(PedidoDesayunoEncargadoDetailView, self).dispatch(*args, **kwargs)
        except:
            return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        pedidoDesayuno = PedidoDesayuno.objects.get(id=pk)
        itemsDesayuno = ItemPedido.objects.filter(pedidoDesayuno= pk)
        context['itemsDesayuno'] = itemsDesayuno
        context['pedidoDesayuno'] = pedidoDesayuno
        return context

class ListaNotificacionesRecibidasResponsable(GroupRequiredMixin, ListView):
    model = Notificacion
    template_name = 'encargado/lista_notificaciones_recibidas_encargado.html'
    group_required = u"Responsable"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        idSesion = self.request.session['_auth_user_id']
        alojamientoDelResponsable = Alojamiento.objects.get(responsable=idSesion)
        context['notificaciones'] = Notificacion.objects.filter(Q(tipo_notificacion__emisor='Infuetur') & (Q(alojamiento=alojamientoDelResponsable) | Q(alojamiento=None)) )
        return context

class ListaNotificacionesEnviadasResponsable(GroupRequiredMixin, ListView):
    model = Notificacion
    template_name = 'encargado/lista_notificaciones_enviadas_encargado.html'
    group_required = u"Responsable"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        idSesion = self.request.session['_auth_user_id']
        alojamientoDelResponsable = Alojamiento.objects.get(responsable=idSesion)
        reservasDelAlojamiento = Reserva.objects.filter(alojamiento=alojamientoDelResponsable)
        context['notificaciones'] = Notificacion.objects.filter(Q(tipo_notificacion__emisor='Responsable') & Q(reserva__in=reservasDelAlojamiento))
        return context

class NotificacionResponsableCreate(GroupRequiredMixin, CreateView):
    template_name = "encargado/notificacion_form_encargado.html"
    model = Notificacion
    form_class = NotificacionResponsableForm
    success_url = reverse_lazy('listaNotificacionesEnviadasResponsable')
    group_required = u"Responsable"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.session['_auth_user_id']
        return kwargs  

class FichaNotificacionResponsable(GroupRequiredMixin, TemplateView):
    template_name = "encargado/ficha_notificacion_encargado.html"
    group_required = u"Responsable"

    def dispatch(self, *args, **kwargs):
        pk = self.kwargs['pk']
        try:
            idSesion = self.request.session['_auth_user_id']
            alojamientoDelResponsable = Alojamiento.objects.get(responsable=idSesion)
            notificacion = Notificacion.objects.get(id=pk)
            if notificacion.tipo_notificacion.emisor == 'Infuetur':
                if ((notificacion.alojamiento == alojamientoDelResponsable) | (notificacion.alojamiento == None)):
                    return super(FichaNotificacionResponsable, self).dispatch(*args, **kwargs)
                else:
                    return redirect('unauthorized')
            else:
                reservasDelAlojamiento = Reserva.objects.filter(alojamiento=alojamientoDelResponsable)
                if notificacion.reserva in reservasDelAlojamiento:
                    return super(FichaNotificacionResponsable, self).dispatch(*args, **kwargs)
                else:
                    return redirect('unauthorized')
        except:
            return redirect('unauthorized')
            

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        try:
            context['notificacion'] = Notificacion.objects.get(id=pk)
        except:
            context['notificacion'] = False
        return context
