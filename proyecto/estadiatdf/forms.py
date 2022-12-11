from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import query
from django.forms import ModelForm
from django.forms import formset_factory
from django.forms import modelformset_factory
from django.forms import fields
#from django.forms.fields import ChoiceField, IntegerField
from django.http import request
from .models import Alojamiento, ConfiguracionDesayuno, DJCovid, FichaIngreso, PedidoDesayuno, Reserva, SolicitudIngresoRapido
from .models import ItemPedido, ItemDesayuno, Notificacion, TipoNotificacion

class SignUpForm(UserCreationForm):
    nombre = forms.CharField(max_length=30, required=False, help_text='Opcional', widget = forms.TextInput(attrs={'class': 'form-control'}))
    apellido = forms.CharField(max_length=30, required=False, help_text='Opcional', widget = forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=254, help_text='Requerido. Escriba un email válido', widget = forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(widget=(forms.PasswordInput(attrs={'class': 'form-control'})))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('username', 'nombre', 'apellido', 'email', 'password1', 'password2', )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EmailTokenForm(forms.Form):
    email = forms.EmailField(max_length=254, help_text='Requerido. Escribe un email válido.', widget= forms.EmailInput(attrs={'class': 'form-control'}))

class SirEncargadoForm(ModelForm):

    class Meta:
        model = SolicitudIngresoRapido
        fields = '__all__'
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'respuesta': forms.TextInput(attrs={'class': 'form-control'}),
            'reserva': forms.HiddenInput()
        }
"""         exclude = ('reserva','fecha_solicitud') """

class ReservaForm(ModelForm):
    
    class Meta:    
        model = Reserva
        exclude = ('alojamiento','token','ingreso_rapido')
        labels = {
            'pax': 'Cantidad de pasajeros'
        }
        widgets = {
            'nombre_huesped': forms.TextInput(attrs={'class': 'form-control'}),
            'origen_reserva': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_reserva': forms.TextInput(attrs={'class': 'form-control'}),
            'pax': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_reservado': forms.DateInput(attrs={'class': 'form-control','type': 'date'}, format='%Y-%m-%d'),
            'fecha_check_in': forms.DateInput(attrs={'class': 'form-control','type': 'date'}, format='%Y-%m-%d'),
            'fecha_check_out': forms.DateInput(attrs={'class': 'form-control','type': 'date'}, format='%Y-%m-%d'),
            'comentario': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_check_in = cleaned_data.get('fecha_check_in')
        fecha_check_out = cleaned_data.get('fecha_check_out')
        if fecha_check_in > fecha_check_out:
            raise forms.ValidationError("La fecha del checkout debe ser mayor que la de checkin.")
        
class FichaIngresoForm(ModelForm):
    class Meta:    
        model = FichaIngreso
        exclude = ('reserva',)
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control','type': 'date'}, format='%Y-%m-%d'),
            'domicilio': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_frente': forms.FileInput(attrs={'class': 'form-control', 'required': False}),
            'foto_reverso': forms.FileInput(attrs={'class': 'form-control', 'required': False}),
        }

class DJCovidForm(ModelForm):
    class Meta:    
        model = DJCovid
        exclude = ('ficha_ingreso','fecha_declaracion')
        labels = {
            'procedencia': 'Lugar de procedencia',
            'zona_riesgos' : '¿Ha estado en alguna de las zonas de riesgo de COVID 19 en los últimos 14 días?',
            'sintomas' : '¿Ha tenido síntomas que podrían estar asociados al COVID 19 en los últimos 14 días?',
            'contacto_covid' : '¿Ha estado en contacto en los últimos 14 días con personas en las que se ha confirmado estar infectadas por COVID 19?',
            'acudido_medico' : '¿Ha acudido en los últimos 14 días a un centro médico u hospitalario como consecuencia de síntomas que podrían estar asociados al COVID 19 y se ha descartado por los facultativos el contagio? ',
            'sospecha' : '¿Tiene motivos para sospechar que podría estar infectado por COVID 19?'
        }
        widgets = {
            'procedencia': forms.TextInput(attrs={'class': 'form-control'}),
            'zona_riesgos' : forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sintomas' : forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'contacto_covid' : forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'acudido_medico' : forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sospecha' : forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class PedidoDesayunoModelForm(forms.ModelForm):
    class Meta:
        model = PedidoDesayuno
        fields = ('horaDesayuno','takeaway','comentario')
        labels = {
            'horaDesayuno': 'Hora de desayuno',
            'takeaway': 'Take away',
            'comentario': 'Comentario'
        }
        widgets = {
            'horaDesayuno': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'type': 'time','min': '07:00', 'max':'10:00'}),
            'takeaway': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'comentario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Comentario'
                }
            )
        }

class ItemPedidoForm(forms.ModelForm):
    class Meta:    
        model = ItemPedido
        fields = ('configuracionDesayuno','cantidad')
        widgets={
                'DELETE': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                'configuracionDesayuno': forms.Select(attrs={'class': 'form-select'}),
            }

ItemPedidoFormset = modelformset_factory(
    ItemPedido,
    #form = ItemPedidoForm,
    fields=('configuracionDesayuno','cantidad'),
    extra=1,
    can_delete=True,
    #formset= ItemPedido.objects.filter(id=7),
    #itemDesayuno = forms.ModelChoiceField(queryset=ItemDesayuno.objects.filter(categoria='Aderezos')),
    widgets={
        'configuracionDesayuno': forms.Select(attrs={'class': 'form-select'}),
        'cantidad': forms.NumberInput(
            attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Cantidad'
            }
        ),
        'DELETE': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }
    
)

class NotificacionINFUETURForm(ModelForm):
    class Meta:    
        model = Notificacion
        exclude = ('reserva','fecha','visto')
        widgets = {
            'tipo_notificacion': forms.Select(attrs={'class': 'form-select'}),
            'alojamiento': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Título'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_notificacion'].queryset = TipoNotificacion.objects.filter(emisor='Infuetur').order_by('nombre')
        self.fields['alojamiento'].queryset = Alojamiento.objects.all().order_by('nombre')

class ItemConfigurarDesayunoForm(forms.Form):
#    id = forms.IntegerField()
    nombre = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly','class':'form-control'}))
    activo = forms.BooleanField(initial=False, required= False)
    widgets = {
        'activo': forms.CheckboxInput(attrs={'class':'form-control'}),
    }

ItemConfigurarDesayunoFormset = formset_factory(
    ItemConfigurarDesayunoForm
)

class NotificacionResponsableForm(ModelForm):
    class Meta:    
        model = Notificacion
        exclude = ('alojamiento','fecha','visto')
        widgets = {
            'tipo_notificacion': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Título'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción'}),
            'reserva': forms.Select(attrs={'class': 'form-select', 'required': True})
        }
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        alojamientoDelResponsable = Alojamiento.objects.get(responsable=user)
        self.fields['reserva'].queryset = Reserva.objects.filter(alojamiento=alojamientoDelResponsable)
        self.fields['tipo_notificacion'].queryset = TipoNotificacion.objects.filter(emisor='Responsable').order_by('nombre')

class DeleteResponsableForm(forms.Form):
    id = forms.IntegerField(widget= forms.HiddenInput())
