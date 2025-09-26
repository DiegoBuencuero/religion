from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.forms import ModelForm, Form
from django.contrib.auth.models import User
from .models import MensajeUsuario, AlertaUsuario, TareaUsuario, Cartera, Comprobante, Caja, AccesoPerfil, Propiedad
from .models import MetodoPago
from django.utils.translation import gettext_lazy as _


class BaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class RegularForm(Form):
    def __init__(self, *args, **kwargs):
        super(RegularForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class LoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control p_input'
    username = forms.CharField(max_length=63)
    password = forms.CharField(max_length=63, widget=forms.PasswordInput)

class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(MyPasswordChangeForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
class MensajeForm(BaseForm):
    def __init__(self, usuario, *args, **kwargs):
        super (MensajeForm,self ).__init__(*args,**kwargs)
        self.fields['usuario_to'].queryset = User.objects.filter(profile__empresa = usuario.profile.empresa).exclude(username = usuario)
        self.fields['usuario_cc'].queryset = User.objects.filter(profile__empresa = usuario.profile.empresa).exclude(username = usuario)

    class Meta:
        model = MensajeUsuario
        fields = '__all__'
        exclude = ['usuario_from', 'timestamp', 'leido', 'leido_cc'] 

class Doacoes(BaseForm):
    from django import forms

class DoacaoForm(forms.Form):
    nome = forms.CharField(label="Nome", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    sobrenome = forms.CharField(label="Sobrenome", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    doar_em_nome_de = forms.CharField(label="Doar em nome de", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefone = forms.CharField(label="Telefone", max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    data_nascimento = forms.DateField(label="Data de nascimento", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    mensagem = forms.CharField(label="Mensagem", required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))


class AsignarAlertaForm(BaseForm):
    def __init__(self, company, *args, **kwargs):
        super (AsignarAlertaForm,self ).__init__(*args,**kwargs)
        self.fields['usuarios'].queryset = User.objects.filter(profile__empresa = company)

    class Meta:
        model = AlertaUsuario
        fields = '__all__'
        exclude = ['usuario']
    usuarios = forms.ModelMultipleChoiceField(queryset=User.objects.all())


class AsignarTareaForm(BaseForm):
    def __init__(self, company, *args, **kwargs):
        super (AsignarTareaForm,self ).__init__(*args,**kwargs)
        self.fields['usuarios'].queryset = User.objects.filter(profile__empresa = company)

    class Meta:
        model = TareaUsuario
        fields = '__all__'
        exclude = ['usuario', 'ordenada_por', 'timestamp']
    usuarios = forms.ModelMultipleChoiceField(queryset=User.objects.all())


class ConfiguracionSistemaForm(RegularForm):
    def __init__(self, company, *args, **kwargs):
        super (ConfiguracionSistemaForm,self ).__init__(*args,**kwargs)
        self.fields['correo_tls'].widget.attrs['class'] = 'form-check-input'
        self.fields['usrmant'].queryset = User.objects.filter(profile__rubroUsuario__codigo = 'MA',  profile__empresa = company)
        #self.fields['listaprecio'].queryset = ListaPrecio.objects.filter(empresa = company)
        self.fields['cartera_dash1'].queryset = Cartera.objects.filter(empresa = company)
        self.fields['comprobante_caja_recibo'].queryset = Comprobante.objects.filter(empresa = company)
        self.fields['comprobante_venta'].queryset = Comprobante.objects.filter(empresa = company)
        self.fields['comprobante_recibo'].queryset = Comprobante.objects.filter(empresa = company)
        self.fields['cartera_recibo'].queryset = Cartera.objects.filter(empresa = company)
        self.fields['mpago_default'].queryset = MetodoPago.objects.filter(empresa = company)
    #listaprecio = forms.ModelChoiceField(queryset=ListaPrecio.objects.all())
    # adic_obl = forms.ChoiceField(choices=[('0', 'No obligatorio'), ('1', 'Obligatorio'),])
    imagen = forms.ImageField(required=False)
    usrmant = forms.ModelChoiceField(queryset=User.objects.all())
    dias_venc_mant = forms.IntegerField(label=_('dias_venc_mant'))
    texto_instalacion = forms.CharField(widget=forms.Textarea, label= _('texto_instalacion'))
    texto_desinstalacion = forms.CharField(widget=forms.Textarea, label= _('texto_desinstalacion'))
    comprobante_recibo = forms.ModelChoiceField(queryset=Comprobante.objects.all(), empty_label='Seleccione una comprobante', help_text='Required')
    cartera_recibo = forms.ModelChoiceField(queryset=Cartera.objects.all(), empty_label='Seleccione una cartera', help_text='Required')
    comprobante_caja_recibo = forms.ModelChoiceField(queryset=Comprobante.objects.all(), empty_label='Seleccione una comprobante', help_text='Required')
    comprobante_venta = forms.ModelChoiceField(queryset=Comprobante.objects.all(), empty_label='Seleccione una comprobante', help_text='Required')
    mpago_default = forms.ModelChoiceField(queryset=MetodoPago.objects.all(), empty_label='Seleccione metodo pago', help_text='Required')
    correo_reserva = forms.CharField(widget=forms.Textarea)
    correo_host = forms.CharField(max_length=100)
    correo_port = forms.IntegerField()
    correo_usuario = forms.CharField(max_length=100)
    correo_pswd = forms.CharField(max_length=100)
    correo_tls = forms.BooleanField(required=False)
    correo_remitente = forms.EmailField()
    eliminar_tareas = forms.BooleanField(required=False)
    dias_tareas_eliminar = forms.IntegerField()
    dias_presu_venc = forms.IntegerField(label=_('dias_venc_presu'))
    dias_mant_venc = forms.IntegerField(label=_('dias_venc_mant'))
    dias_caja_venc = forms.IntegerField(label=_('dias_caja_venc'))
    cant_dias_def_venc = forms.IntegerField(label=_('cant_dias_def_venc'))
    cartera_dash1 = forms.ModelChoiceField(queryset=Cartera.objects.all(), label=_('cartera_dash_vencimientos'))
    inicio_bisemana = forms.DateField(label=_('Inicio bisemana'), required=True, widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'placeholder': 'Seleccione una fecha'}))


class ConfiguracionForm(RegularForm):
    def __init__(self, *args, **kwargs):
        super (ConfiguracionForm,self ).__init__(*args,**kwargs)
    nombre = forms.CharField(max_length=30)
    apellido = forms.CharField(max_length=30)
    email = forms.EmailField()
    imagen = forms.ImageField(required=False)



    ################## --------------------FORMS PROPIEDADES -----------------------------------------

class PropiedadABMForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super(PropiedadABMForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Propiedad
        fields = '__all__'
        exclude = ['empresa'] 
