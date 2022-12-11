from django.views.generic.base import TemplateView
# from django.views.generic import ListView, DetailView
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from ..models import Alojamiento, Contacto, Notificacion
from django.db.models import Q

from ..forms import EmailTokenForm, NotificacionINFUETURForm, DeleteResponsableForm
#from django.views.generic.edit import FormMixin
from django.urls import reverse
from django.core.mail import send_mail
import uuid

from django.http import HttpResponseRedirect

from braces.views import GroupRequiredMixin


class ListaAlojamientos(GroupRequiredMixin, ListView):
    model = Alojamiento
    template_name = 'infuetur/listaAloja.html'
    group_required = u"AdminINFUETUR"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alojamientos'] = Alojamiento.objects.all

        return context

class FichaAlojamiento(GroupRequiredMixin, TemplateView):
    template_name = 'infuetur/detalleAloja.html'
    group_required = u"AdminINFUETUR"

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        context = super().get_context_data(**kwargs)

        alojamiento = Alojamiento.objects.get(id=pk)
        context['alojamiento'] = alojamiento
        contactos = Contacto.objects.filter(alojamiento_id=pk)
        context['contactos'] = contactos
        emails = contactos.filter(tipo__contains='mail')
        context['emails'] = emails
        try:
            responsable = User.objects.get(alojamiento=pk)
            context['responsable'] = responsable
        except:
            context['responsable'] = False
        form = EmailTokenForm(self.request.POST or None)
        context['form'] = form
        form_delete = DeleteResponsableForm(self.request.POST or None)
        context['form_delete'] = form_delete
        context['pk'] = pk
        return context
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        pk = context['pk']
        form = context['form']
        form_delete = context['form_delete']
        if request.method=='POST' and 'enviarEmail' in request.POST:
            if form.is_valid():
                # Generacion de Token y envio de link
                alojamiento = Alojamiento.objects.get(pk=self.kwargs['pk'])
                alojamiento.token = uuid.uuid4()
                alojamiento.save()
                subject = "Registro de Responsable Estadia Segura TDF"
                message = "Para registrar su usuario ingrese al siguiente link: " + "http://127.0.0.1:8000/signup?uuid=" + str(alojamiento.token)
                from_email = "registro@estadiasegura.tur.ar"
                recipient_list = [form.cleaned_data['email']]
                try:
                    send_mail(subject, message, from_email, recipient_list)
                except:
                    pass
                try:
                    responsable = User.objects.get(alojamiento=pk)
                    responsable.delete()
                except:
                    pass
                return HttpResponseRedirect(reverse('fichaAlojamiento', kwargs={'pk': pk}))
        if request.method=='POST' and 'eliminarResponsable' in request.POST:
            if form_delete.is_valid():
                idResponsable = form_delete.cleaned_data['id']
                responsable = User.objects.get(id=idResponsable)
                responsable.delete()
                return HttpResponseRedirect(reverse('fichaAlojamiento', kwargs={'pk': pk}))
        return super(TemplateView, self).render_to_response(context)

class ListaNotificacionesINFUETUR(GroupRequiredMixin, ListView):
    model = Notificacion
    template_name = 'infuetur/listaNotificaciones.html'
    group_required = u"AdminINFUETUR"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
#        context['notificaciones'] = Notificacion.objects.filter(Q(tipo_notificacion__nombre="Situación epidemiológica")|Q(tipo_notificacion__nombre="Protocolo COVID"))
        context['notificaciones'] = Notificacion.objects.filter(tipo_notificacion__emisor='Infuetur')
        return context

class NotificacionInfueturCreate(GroupRequiredMixin, CreateView):
    template_name = "infuetur/notificacion_form.html"
    model = Notificacion
    form_class = NotificacionINFUETURForm
    success_url = reverse_lazy('listaNotificacionesINFUETUR')
    # Debería redirigir a la vista de la notificación nueva
    group_required = u"AdminINFUETUR"

class FichaNotificacionInfuetur(GroupRequiredMixin, TemplateView):
    template_name = "infuetur/ficha_notificacion_infuetur.html"
    group_required = u"AdminINFUETUR"

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        try:
            context['notificacion'] = Notificacion.objects.get(id=pk)
        except:
            context['notificacion'] = False
        return context

class EnviarEmail(TemplateView):
    template_name = "bienvenida/bienvenida.html"

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        context['id'] = pk
