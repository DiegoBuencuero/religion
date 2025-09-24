from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from .choices import OPCIONES_COMPROBANTES, OPCIONES_SALDO
from django.db import models
from django.contrib.auth.models import User  

class Pais(models.Model):
    def __str__(self):
        return self.descripcion
    codigo = models.CharField( max_length=2, verbose_name=_("codigo") )
    descripcion = models.CharField( max_length=100, verbose_name=_("descripcion"))

class Empresa(models.Model):
    def __str__(self):
        return str(self.razon_social)
    razon_social = models.CharField(max_length=100)
    nombre_fantasia = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    telefono = models.CharField(max_length=30)
    movil = models.CharField(max_length=30)
    email = models.EmailField()
    cuit = models.CharField(max_length=50)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    logo = models.ImageField(default='default.jpg', upload_to='logos')
    last_process = models.DateTimeField(default=timezone.now)

class RubroUsuario(models.Model):
    def __str__(self):
        return str(self.descripcion)
    codigo = models.CharField(max_length=2)
    descripcion = models.CharField(max_length=50)

class Profile(models.Model):
    def __str__(self):
        return str(self.user.username)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    rubroUsuario = models.ForeignKey(RubroUsuario, on_delete=models.CASCADE, null=True, blank=True)






class TipoPropiedad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Propiedad(models.Model):
    def __str__(self):
        return f"{self.titulo} - {self.empresa.razon_social}"
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name=_('empresa'))
    tipo = models.ForeignKey(TipoPropiedad, on_delete=models.CASCADE, related_name="propiedades" )
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=15, decimal_places=2)
    dormitorios = models.IntegerField(blank=True, null=True)
    banos = models.IntegerField(blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

 
class ImagenPropiedad(models.Model):
    def __str__(self):
        return f"Imagen de {self.propiedad.titulo} ({'Principal' if self.es_principal else 'Secundaria'})"
    propiedad = models.ForeignKey( Propiedad, on_delete=models.CASCADE, related_name="imagenes" )
    imagen = models.ImageField(upload_to="propiedades/")  
    orden = models.PositiveIntegerField(default=0)
    es_principal = models.BooleanField(default=False) 








class Provincia(models.Model):
    def __str__(self):
        return self.pais.descripcion + ' - ' +self.descripcion
    pais = models.ForeignKey( Pais, on_delete=models.CASCADE, verbose_name=_("pais"))
    codigo = models.CharField(max_length=5, verbose_name=_("codigo"))
    descripcion = models.CharField(max_length=100, verbose_name=_("descripcion"))

# Create your models here.



class Municipio(models.Model):
    def __str__(self):
        return self.descripcion
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    provincia = models.ForeignKey( Provincia, on_delete=models.CASCADE, verbose_name=_("provincia"))
    descripcion = models.CharField(max_length=100, verbose_name=_("descripcion"))

class Ciudad (models.Model):
    def __str__(self):
        return self.descripcion
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    municipio = models.ForeignKey( Municipio, on_delete=models.CASCADE, verbose_name=_("municipio"))
    descripcion = models.CharField(max_length=100, verbose_name=_("descripcion"))

class Barrio (models.Model):
    def __str__(self):
        return self.ciudad.descripcion + ' - ' + self.descripcion
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    ciudad = models.ForeignKey( Ciudad, on_delete=models.CASCADE, verbose_name=_("ciudad"))
    descripcion = models.CharField(max_length=100, verbose_name=_("descripcion"))






@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Configuracion(models.Model):
    def __str__(self):
        return str(self.parametro)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    parametro = models.CharField(max_length=8)
    valor = models.TextField()


class Comprobante(models.Model):
    def __str__(self):
        return str(self.descripcion)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=50, verbose_name=_("descripcion"))
    abrev = models.CharField(max_length=5, unique=True, verbose_name=_("abrev"))
    signo = models.CharField(max_length=1,verbose_name=_("signo"), choices=OPCIONES_COMPROBANTES)
    automatico = models.BooleanField(default=True, verbose_name=_("automatico"))
    numero = models.IntegerField(null=True, blank=True, verbose_name=_("numero"))


class Cartera(models.Model):
    def __str__(self):
        return str(self.nombre)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50, verbose_name=_("nombre"))
    abrev = models.CharField(max_length=5, unique=True, verbose_name=_("Abrev"))
    t_saldo = models.CharField(max_length=1, verbose_name = 'Tipo de saldo', choices=OPCIONES_SALDO)

class MetodoPago(models.Model):
    def __str__(self):
        return str(self.descripcion)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=80)
    desc_abr = models.CharField(max_length=3)
    cartera = models.ForeignKey("Cartera", on_delete=models.CASCADE, null=True, blank=True)


# Modelo para representar los gastos
class Caja(models.Model):
    def __str__(self):
        return str(self.descripcion)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    descripcion = models.TextField( blank=True)
    comprobante = models.ForeignKey(Comprobante, on_delete=models.CASCADE)
    numero = models.IntegerField(default=0)
    debe = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    haber = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.CASCADE, null=True, blank=True)
    cartera = models.ForeignKey(Cartera, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)
    vencimiento = models.DateField(default=timezone.now, verbose_name=_("vencimiento"))
    timestamp = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)


class TareaUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tarea = models.CharField(max_length=100)
    completada = models.BooleanField(default=False)
    ordenada_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tarea_ordenada_por_usuario')
    timestamp = models.DateTimeField(default=timezone.now)


class MensajeUsuario(models.Model):
    usuario_from = models.ForeignKey(User, on_delete=models.CASCADE)
    usuario_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_usuario_to')
    usuario_cc = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_usuario_cc', null=True, blank=True)
    asunto = models.CharField(max_length=100)
    texto = models.TextField()
    leido = models.BooleanField(default=False)
    leido_cc = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)


class CategoriaAlerta(models.Model):
    def __str__(self):
        return str(self.nombre)
    nombre = models.CharField(max_length=50)
    class_img = models.CharField(max_length=20, null=True, blank=True)
    color = models.CharField(max_length=20, choices=[('danger', 'Danger'),('success', 'Success'), ('info', 'Info')], null=True, blank=True)

class AlertaUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(CategoriaAlerta, on_delete=models.CASCADE, null=True, blank=True)
    texto = models.CharField(max_length=30)


class Pantalla(models.Model):
    def __str__(self):
        return str(self.nombre)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100, default='')
    vista = models.CharField(max_length=100)

class AccesoPerfil(models.Model):
    def __str__(self):
        return str(self.empresa) + ' ' + str(self.rubroUsuario) + ' ' + str(self.pantalla)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    rubroUsuario = models.ForeignKey(RubroUsuario, on_delete=models.CASCADE, null=True, blank=True)
    pantalla = models.ForeignKey(Pantalla, on_delete=models.CASCADE)
    acceso = models.BooleanField()
    alta = models.BooleanField()
    baja = models.BooleanField()
    modificar = models.BooleanField()