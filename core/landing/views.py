from django.shortcuts import render
from calendar import month_name, monthrange
from django.utils import timezone, translation
from dateutil.relativedelta import relativedelta
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import date, timedelta, datetime
from .models import Configuracion, Cartera, Caja, TareaUsuario, MensajeUsuario, AlertaUsuario, Comprobante, Propiedad
from .models import Pantalla, AccesoPerfil
from .forms import LoginForm, MyPasswordChangeForm, MensajeForm, AsignarAlertaForm, AsignarTareaForm, ConfiguracionSistemaForm, ConfiguracionForm,  DoacaoForm
from .forms import PropiedadABMForm
#from .forms import ComprobanteABMForm, CarteraABMForm, MovimientosCajaForm, AccesoABMForm
from decimal import Decimal
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.http import JsonResponse
import json
from django.db.models import Q
from django.contrib.auth.models import User
from django.apps import apps
from django.utils import timezone
from django.contrib import messages


##---------------------LOGIN--------------------
def login_view(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request,'login.html', {'form': form})
    
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request,username=username,password=password)
            if user:
                login(request, user)
                return redirect('/')
            else:
                form.add_error('username', 'Usuario o password no validos.')
        
        return render(request,'login.html',{'form': form})


##---------------------NAV--------------------
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def doacoes(request):
    if request.method == "POST":
        form = DoacaoForm(request.POST)
        if form.is_valid():
            # Guardar o procesar la donación
            messages.success(request, "🙏 Obrigado pela sua doação!")
    else:
        form = DoacaoForm()
    return render(request, "doacoes.html", {"form": form})
def blog(request):
    return render(request, 'blog.html')

def musicas(request):
    return render(request, 'musicas.html')


def news_list(request):
    return render(request, 'news.html')


def news_create(request):
    return render(request, 'news_create.html')

def contact(request):
    return render(request, 'contact.html')


##---------------------DESPLEGABLE USUARIO LOGUEADO--------------------
def favorite(request):
    return render(request, 'favorite.html')

def map(request):
    empresa = request.user.profile.empresa
    propiedades = Propiedad.objects.filter(empresa=empresa)

    vector = []
    for p in propiedades:
        vector.append({
            "lat": float(p.latitud) if p.latitud else None,
            "lng": float(p.longitud) if p.longitud else None,
            "titulo": p.titulo,
            "ciudad": p.ciudad,
            "pais": p.pais,
            "precio": float(p.precio) if p.precio else None,
        })

    return render(request, "map.html", {
        "locations": json.dumps(vector)  
    })

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def my_properties(request):
    return render(request, 'my_properties.html')

@login_required
def chat_support(request):
    return render(request, 'chat_support.html')

@login_required
def hidden_listings(request):
    return render(request, 'hidden_listings.html')

@login_required
def settings_view(request):
    return render(request, 'settings.html')

@login_required
def profile_view(request):
    return render(request, 'profile.html')






def es_superuser(usuario):
    return usuario.is_superuser

def es_staff(usuario):
    return usuario.is_staff

def access_not_allowed(request):
    return render(request, 'error_usuario.html', {'error_number': 63, 'error_desc': 'Acceso no permitido'})    

def access_check(usuario, pantalla_nombre, acceso = True, alta = False, baja = False, modificar = False):
    empresa = usuario.profile.empresa
    rubro_usuario = usuario.profile.rubroUsuario
    try:
        pantalla = Pantalla.objects.get(vista = pantalla_nombre)
    except:
        return True
    try:
        acceso_usuario = AccesoPerfil.objects.get(empresa = empresa, rubroUsuario = rubro_usuario, pantalla = pantalla)
    except:
        return True
    retval = True
    if acceso:
        if not acceso_usuario.acceso:
            retval = False
    if retval:
        if alta:
            if not acceso_usuario.alta:
                retval = False
    if retval:
        if baja:
            if not acceso_usuario.baja:
                retval = False
    if retval:
        if modificar:
            if not acceso_usuario.modificar:
                retval = False
        
    return retval
    

def obtener_dias_en_mes(anio, mes):
    _, dias_en_mes = monthrange(anio, mes)
    return dias_en_mes

def obtener_proximos_meses(cantidad):
    anio_actual = timezone.now().year
    primero_de_enero = timezone.datetime(anio_actual, 1, 1)
    ahora = primero_de_enero
    proximos_meses = []

    for i in range(0, cantidad ):
        # Calcula la fecha del próximo mes de manera precisa
        fecha_proximo_mes = ahora + relativedelta(months=i)

        # Obtiene el nombre del mes
        nombre_proximo_mes = month_name[fecha_proximo_mes.month]

        proximos_meses.append(nombre_proximo_mes)

    return proximos_meses

def get_conf_param(company, parametro, default=None):
    try:
        check_conf = Configuracion.objects.get(parametro = parametro, empresa = company)
        valor = check_conf.valor
    except:
        if default is not None:
            valor = ''
        else:
            valor = default
    return valor


def get_logic_param(company, parametro, default= None):
    valor = get_conf_param(company, parametro, default)
    if parametro == 'car_caja':
        if valor == '':
            return None
        else:
            try:
                cartera_caja = Cartera.objects.get(id = int(valor))
                return cartera_caja
            except:
                return None

    elif parametro == 'pre_dias':
        if valor == '':
            retvalue = 5
        else:
            try:
                retvalue = int(valor)
            except:
                retvalue = 5
        return retvalue
    elif parametro == 'man_dias':
        if valor == '':
            retvalue = 5
        else:
            try:
                retvalue = int(valor)
            except:
                retvalue = 5
        return retvalue
    elif parametro == 'ven_dias':
        if valor == '':
            retvalue = 5
        else:
            try:
                retvalue = int(valor)
            except:
                retvalue = 5
        return retvalue
    elif parametro == 'dias_ven':
        if valor == '':
            retvalue = 30
        else:
            try:
                retvalue = int(valor)
            except:
                retvalue = 30
        return retvalue
    elif parametro == 'car_das1':
        if valor == '':
            retvalue = ''
        else:
            try:
                retvalue = Cartera.objects.get(id=int(valor))
            except:
                retvalue = ''
        return retvalue
    else:
        return valor


def save_conf_param(company, parametro, valor):
    try:
        check_conf = Configuracion.objects.get(parametro = parametro, empresa = company)
        check_conf.valor = valor
        check_conf.save()
    except:
        conf = Configuracion()
        conf.parametro = parametro
        conf.valor = valor
        conf.empresa = company
        conf.save()

def ceronull(valor):
    if valor is None:
        return 0
    else:
        return valor
def obtener_saldo_cartera(cartera):
    registros = Caja.objects.filter(cartera = cartera)
    saldo = 0
    for r in registros:
        saldo += (ceronull(r.debe) - ceronull(r.haber))
    return saldo

def cartera_mostrador(company):
    return get_logic_param(company, 'car_caja')

@login_required
def home(request):
    empresa = request.user.profile.empresa
    ahora = timezone.now()
    hoy = ahora.date()
    fecha_proximo_mes = ahora + relativedelta(months=1)





  
    

    return render(request, 'index.html', )

    empresa = request.user.profile.empresa
    fecha_inicio_anio = date(date.today().year, 1, 1)
    terrenos = Terreno.objects.filter(empresa=empresa)
    gastos = gastosOOH.objects.filter(ooh__terreno__empresa=empresa, fecha__gte=fecha_inicio_anio)
    detalles = PresupuestoDetalle.objects.select_related('presupuesto').filter(presupuesto__empresa=empresa, presupuesto__estado='A')   

    total_ventas = 0
    total_alquiler = 0
    total_gastos_rubros = 0
    total_gastos = 0
    ventas_por_tipo = {}
  
    #ventas
    for detalle in detalles:
        valor_grafica = float(detalle.presupuesto.valorGrafica)
        descuento = float(detalle.presupuesto.descuento)
        cantidad = detalle.cantidad
        parcial = float(detalle.parcial)     
        tipo = detalle.ooh.tipologia   

        total_detalles = valor_grafica + (parcial * cantidad) - (descuento * cantidad)

        total_ventas += total_detalles

        if tipo in ventas_por_tipo:
            ventas_por_tipo[tipo] += total_detalles
        else:
            ventas_por_tipo[tipo] = total_detalles

    for tipo, ventas in ventas_por_tipo.items():
        ventas_por_tipo[tipo] = (ventas / total_ventas) * 100 if total_ventas > 0 else 0

      #gastos
    for gasto in gastos:
        total_gastos_rubros += float(gasto.monto)
    
    # alquileres      
    for terreno in terrenos: 
        alquileres = TerrenoAlquiler.objects.filter(terreno=terreno)     
        total_terreno_alquiler = 0
        for alquiler in alquileres:
            total_alquiler += float(alquiler.valor_alquiler)
        total_alquiler += total_terreno_alquiler
    
    total_gastos = total_alquiler + total_gastos_rubros        

    gastos_ingresos = {
        'total_ventas': str(total_ventas).replace(',', '.'),
        'total_gastos': str(total_gastos).replace(',', '.'),
        'ventas_por_tipo': ventas_por_tipo
    }
    
    return gastos_ingresos


    empresa = request.user.profile.empresa
    fecha_inicio_anio = date(date.today().year, 1, 1)    
    mantenimientos = Mantenimiento.objects.filter(empresa=empresa, fecha__gte=fecha_inicio_anio)
    
    total_acumulado_anual = 0
    total_terminado = 0
    
    tipos_excluidos = ['Instalación', 'Desinstalación']
    
    for mantenimiento in mantenimientos:
        if mantenimiento.tipoMantenimiento not in tipos_excluidos:
            total_acumulado_anual += 1  
            
            if mantenimiento.estado == 'T':  
                total_terminado += 1      
   
    if total_acumulado_anual > 0:
        porcentaje_terminado = (total_terminado / total_acumulado_anual) * 100
        porcentaje_faltante = 100 - porcentaje_terminado
    else:
        porcentaje_terminado = 0
        porcentaje_faltante = 100
    
    return {
        'porcentaje_terminado': str(porcentaje_terminado).replace(',','.'),
        'porcentaje_faltante': str(porcentaje_faltante).replace(',','.')
    }


    pass

# def procesoDiario(usuario):
#     fecha_ayer = timezone.now() - timedelta(days=1)
#     empresa = usuario.profile.empresa
#     if empresa.last_process <= fecha_ayer:
#         presupuestos = Presupuesto.objects.filter(empresa=empresa, fechaValidadReserva__lte=fecha_ayer).exclude(estado='A')
#         for presupuesto in presupuestos:
#             OOHOcupacion.objects.filter(presupuesto=presupuesto).delete()
#             presupuesto.estado = 'V'
#             presupuesto.save()
#         empresa.last_process = timezone.now()
#         empresa.save()






@login_required
def ajax_save_tarea(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        tarea = data.get('tarea')
        nueva_tarea = TareaUsuario()
        nueva_tarea.usuario = request.user
        nueva_tarea.tarea = tarea
        nueva_tarea.ordenada_por = request.user
        nueva_tarea.save()
        response_data = {'response': 0, 'codigo': nueva_tarea.id, 'mensaje': 'alta OK'}
        return JsonResponse(response_data)
    else:
        return JsonResponse({'mensaje': 'Metodo no permitido'}, status=405)
    
@login_required
def ajax_completar_tarea(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tarea_id = data.get('codigo')
            tarea = TareaUsuario.objects.get(id = tarea_id)
            if tarea.completada:
                tarea.completada = False
            else:
                tarea.completada = True
            tarea.save()
            response_data = {'response': 0, 'mensaje': 'alta OK'}
            return JsonResponse(response_data)
        except:
            return JsonResponse({'mensaje': 'Error en tarea'}, status=405)    
    else:
        return JsonResponse({'mensaje': 'Metodo no permitido'}, status=405)
    
@login_required
def ajax_borrar_tarea(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tarea_id = data.get('codigo')
            tarea = TareaUsuario.objects.get(id = tarea_id)
            if tarea.ordenada_por == request.user:
                tarea.delete()
                response_data = {'response': 0, 'mensaje': 'alta OK'}
                return JsonResponse(response_data)
            else:
                return JsonResponse({'mensaje': 'No se permite borrar tareas no asignadas a si mismo'}, status=405)
        except:
            return JsonResponse({'mensaje': 'Error en tarea'}, status=405)    
    else:
        return JsonResponse({'mensaje': 'Metodo no permitido'}, status=405)
    


@login_required
def ajax_obtener_notificaciones(request):
    alertas = AlertaUsuario.objects.filter(usuario = request.user)
    data_alertas = []
    for alerta in alertas:
        data_alertas.append({'texto': alerta.texto, 
                             'codigo':alerta.id, 
                             'categoria': alerta.categoria.nombre,
                             'imagen': alerta.categoria.class_img,
                             'color': alerta.categoria.color,
                             })
    response_data = {'response': 0, 'alertas': data_alertas}        
    return JsonResponse(response_data)
    

@login_required
def ajax_borrar_alerta(request):
    try:
        alert_id = int(request.GET.get('codigo'))
        alerta = AlertaUsuario.objects.get(id=alert_id)
        alerta.delete()
        response_data = {'response': 0, 'mensaje': 'baja OK'}
        return JsonResponse(response_data)
    except:
        return JsonResponse({'mensaje': 'Error en baja alerta'}, status=405)    

@login_required
def crear_mensaje_usuario(request):
    retorno = ''
    if request.method == 'POST':
        form = MensajeForm(request.user, request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.usuario_from = request.user
            mensaje.save()
            return redirect(request.POST.get('url_origen'))
    else:
        form = MensajeForm(request.user)
        retorno = request.GET.get('url_origen')
    context = {
        'form': form,
        'retorno': retorno,
    }
    return render(request, 'crear_mensaje_usuario.html', context)



def tiempo_transcurrido(fecha_hora):
    ahora = timezone.now()
    
    diferencia = ahora - fecha_hora

    # Obtener los componentes de la diferencia
    dias = diferencia.days
    horas, segundos = divmod(diferencia.seconds, 3600)
    minutos, segundos = divmod(segundos, 60)

    if dias > 0:
        if dias == 1:
            return f"{dias} día atrás"
        else:
            return f"{dias} días atrás"
    elif horas > 0:
        if horas == 1:
            return f"{horas} hora atrás"
        else:
            return f"{horas} horas atrás"
    elif minutos > 0:
        if minutos == 1:
            return f"{minutos} minuto atrás"
        else:
            return f"{minutos} minutos atrás"
    else:
        if segundos == 1:
            return f"{segundos} segundo atrás"
        else:
            return f"{segundos} segundos atrás"


@login_required
def ajax_obtener_mensajes(request):
    mensajes = MensajeUsuario.objects.filter(Q(usuario_to = request.user, leido=False) | Q(usuario_cc = request.user, leido_cc = False))
    data_mensajes = []
    for mensaje in mensajes:
        if mensaje.usuario_cc is None:
            cc = None
        else:
            cc = mensaje.usuario_cc.first_name
        if (mensaje.usuario_to == request.user):
            copiado = '0'
        else:
            copiado = '1'
        tiempo = tiempo_transcurrido(mensaje.timestamp)
        data_mensajes.append({'from': mensaje.usuario_from.first_name, 
                             'to':mensaje.usuario_to.first_name, 
                             'cc': cc,
                             'imagen': mensaje.usuario_from.profile.image.url,
                             'texto': mensaje.texto,
                             'hace': tiempo,
                             'copiado': copiado,
                             'codigo': mensaje.id,
                             'asunto': mensaje.asunto,
                             })
    response_data = {'response': 0, 'mensajes': data_mensajes}        
    return JsonResponse(response_data)



@login_required
def ajax_leer_mensaje(request):
    try:
        mensaje_id = int(request.GET.get('codigo'))
        mensaje = MensajeUsuario.objects.get(id=mensaje_id)
        if mensaje.usuario_to == request.user:
            mensaje.leido = True
        if mensaje.usuario_cc == request.user:
            mensaje.leido_cc = True
        mensaje.save()
        response_data = {'response': 0, 'mensaje': 'leido OK'}
        return JsonResponse(response_data)
    except:
        return JsonResponse({'mensaje': 'Error en lectura de mensaje'}, status=405)    



@login_required
def ChangePassword(request):
   form = MyPasswordChangeForm(user=request.user, data=request.POST or None)
   if form.is_valid():
     form.save()
     update_session_auth_hash(request, form.user)
     return redirect('/')
   return render(request, 'change_password.html', {'form': form})




@login_required
def ajax_get_alerta_data(request):
    try:
        alerta_id = int(request.GET.get('alerta'))
        alerta = AlertaUsuario.objects.get(id = alerta_id)
        obj_data = {
            key: value for key, value in alerta.__dict__.items() if isinstance(value, (int, str, bool, float, Decimal))
        }
        data = {'response': 0, 'data': obj_data}
    except:
        data = {'response': 1, 'data': None}
    return JsonResponse(data)


@login_required
@user_passes_test(es_staff )
def asignar_alertas(request):
    alertas = AlertaUsuario.objects.all().order_by('usuario')
    alta = False
    if request.method == 'POST':
        if request.POST.get('registro_id') != '':
            try:
                obj_id = int(request.POST.get('registro_id'))
                objeto = AlertaUsuario.objects.get(id = obj_id)
                form = AsignarAlertaForm(request.user.profile.empresa, request.POST, instance = objeto)
            except:
                return redirect('asignar_alertas')
        else:        
            form = AsignarAlertaForm(request.user.profile.empresa, request.POST)
            alta = True
        if form.is_valid():
            if request.POST.get('eliminar'):
                objeto.delete()
            else:
                origen = form.save(commit=False)
                if alta:
                    for usuario in form.cleaned_data['usuarios']:
                        alerta_nueva = AlertaUsuario()
                        alerta_nueva.usuario = usuario
                        alerta_nueva.categoria = origen.categoria
                        alerta_nueva.texto = origen.texto
                        alerta_nueva.save()
                else:
                    origen.save()
            form = AsignarAlertaForm(request.user.profile.empresa)            
    else:                
        form = AsignarAlertaForm(request.user.profile.empresa)
    context = {
        'alertas':alertas,
        'form': form,
    }
    return render(request, 'asignar_alertas.html', context)


@login_required
def ajax_get_tarea_data(request):
    try:
        tarea_id = int(request.GET.get('tarea'))
        tarea = TareaUsuario.objects.get(id = tarea_id)
        obj_data = {
            key: value for key, value in tarea.__dict__.items() if isinstance(value, (int, str, bool, float, Decimal, datetime))
        }
        obj_data['tiempo'] = tiempo_transcurrido(tarea.timestamp)
        data = {'response': 0, 'data': obj_data}
    except:
        data = {'response': 1, 'data': None}
    return JsonResponse(data)


@login_required
@user_passes_test(es_staff)
def asignar_tareas(request):
    tareas = TareaUsuario.objects.all().order_by('usuario')
    alta = False
    if request.method == 'POST':
        if request.POST.get('registro_id') != '':
            try:
                obj_id = int(request.POST.get('registro_id'))
                objeto = TareaUsuario.objects.get(id = obj_id)
                form = AsignarTareaForm(request.user.profile.empresa, request.POST, instance = objeto)
            except:
                return redirect('asignar_alertas')
        else:        
            form = AsignarTareaForm(request.user.profile.empresa, request.POST)
            alta = True
        if form.is_valid():
            if request.POST.get('eliminar'):
                objeto.delete()
            else:
                origen = form.save(commit=False)
                if alta:
                    for usuario in form.cleaned_data['usuarios']:
                        tarea_nueva = TareaUsuario()
                        tarea_nueva.usuario = usuario
                        tarea_nueva.tarea = origen.tarea
                        tarea_nueva.completada = origen.completada
                        tarea_nueva.ordenada_por = request.user
                        tarea_nueva.save()
                else:
                    origen.save()
            form = AsignarTareaForm(request.user.profile.empresa)            
    else:                
        form = AsignarTareaForm(request.user.profile.empresa)
    context = {
        'tareas':tareas,
        'form': form,
    }
    return render(request, 'asignar_tareas.html', context)


# @login_required
# @user_passes_test(es_staff)
# def configuracion_sistema(request):
#     empresa = request.user.profile.empresa
#     if request.method == 'GET':
#         try:
#             check_conf = Configuracion.objects.get(parametro = 'listprec', empresa = request.user.profile.empresa)
#             id_lista = int(check_conf.valor)
#             listaprecio = ListaPrecio.objects.get(id = id_lista)
#         except:
#             listaprecio = None
#         imagen = request.user.profile.empresa.logo
#         valor = get_conf_param(request.user.profile.empresa, 'usrmant')
#         if valor == '':
#             usrmant = request.user

#         else:
#             try:
#                 usrmant = User.objects.get(id=int(valor))
#             except:
#                 usrmant = request.user

#         valor = get_conf_param(request.user.profile.empresa, 'dvmant')
#         if valor == '':
#             dias_venc_mant = 5
#         else:
#             try:
#                 dias_venc_mant = int(valor)
#             except:
#                 dias_venc_mant = 5
#         valor = get_conf_param(request.user.profile.empresa, 'txtins')
#         if valor == '':
#             texto_instalacion = ''
#         else:
#             texto_instalacion = valor
#         valor = get_conf_param(request.user.profile.empresa, 'txtdeins')
#         if valor == '':
#             texto_desinstalacion = ''
#         else:
#             texto_desinstalacion = valor

#         valor = get_conf_param(request.user.profile.empresa, 'tar_elim')
#         if valor == '':
#             tar_elim = False
#         else:
#             tar_elim = valor
#         if tar_elim:
#             valor = get_conf_param(request.user.profile.empresa, 'tar_dias')
#             if valor == '':
#                 tar_dias = 0
#             else:
#                 try:
#                     tar_dias = int(valor)
#                 except:
#                     tar_dias = 0
#         else:
#             tar_dias = ''


#         valor = get_logic_param(request.user.profile.empresa, 'ini_bise')
#         if valor is None:
#             ini_bise = timezone.now().date()
#         else:
#             ini_bise = datetime.strptime(valor, "%Y-%m-%d")

#         pre_dias = get_logic_param(request.user.profile.empresa, 'pre_dias')
#         man_dias = get_logic_param(request.user.profile.empresa, 'man_dias')

#         ven_dias = get_logic_param(request.user.profile.empresa, 'ven_dias')
#         dias_ven = get_logic_param(request.user.profile.empresa, 'dias_ven')

#         car_das1 = get_logic_param(request.user.profile.empresa, 'car_das1')

#         valor = get_conf_param(request.user.profile.empresa, 'comrecbo')
#         if valor == '':
#             comprobante_recibo = ''
#         else:
#             comprobante_recibo = valor


#         valor = get_conf_param(request.user.profile.empresa, 'carrecbo')
#         if valor == '':
#             cartera_recibo = ''
#         else:
#             cartera_recibo = valor

#         valor = get_conf_param(request.user.profile.empresa, 'comcarec')
#         if valor == '':
#             comprobante_caja_recibo = ''
#         else:
#             comprobante_caja_recibo = valor

#         valor = get_conf_param(request.user.profile.empresa, 'comvent')
#         if valor == '':
#             comprobante_venta = ''
#         else:
#             comprobante_venta = valor

#         valor = get_conf_param(request.user.profile.empresa, 'mpdefau')
#         if valor == '':
#             mpdefau = ''
#         else:
#             mpdefau = valor
#         valor = get_conf_param(request.user.profile.empresa, 'resvcorr')
#         if valor == '':
#             resvcorr = ''
#         else:
#             resvcorr = valor
#         valor = get_conf_param(request.user.profile.empresa, 'corrhost')
#         if valor == '':
#             corrhost = ''
#         else:
#             corrhost = valor
#         valor = get_conf_param(request.user.profile.empresa, 'corrport')
#         if valor == '':
#             corrport = ''
#         else:
#             corrport = valor
#         valor = get_conf_param(request.user.profile.empresa, 'corruser')
#         if valor == '':
#             corruser = ''
#         else:
#             corruser = valor
#         valor = get_conf_param(request.user.profile.empresa, 'corrpswd')
#         if valor == '':
#             corrpswd = ''
#         else:
#             corrpswd = valor

#         valor = get_conf_param(request.user.profile.empresa, 'corrtls')
#         if valor == '':
#             corrtls = False
#         else:
#             if valor == 'True':
#                 corrtls = True
#             else:
#                 corrtls = False

#         valor = get_conf_param(request.user.profile.empresa, 'corrrmte')
#         if valor == '':
#             corrrmte = ''
#         else:
#             corrrmte = valor

#         inicial = {
#             'listaprecio': listaprecio,
#             # 'adic_obl': adic_obl,
#             'imagen':imagen,
#             'usrmant': usrmant,
#             'dias_venc_mant': dias_venc_mant,
#             'texto_instalacion': texto_instalacion,
#             'texto_desinstalacion': texto_desinstalacion,
#             'comprobante_recibo': comprobante_recibo,
#             'cartera_recibo': cartera_recibo,
#             'comprobante_caja_recibo': comprobante_caja_recibo,
#             'comprobante_venta': comprobante_venta,
#             'mpago_default': mpdefau,
#             'eliminar_tareas': tar_elim,
#             'dias_tareas_eliminar': tar_dias,
#             'correo_reserva': resvcorr,
#             'correo_host':corrhost,
#             'correo_port': corrport,
#             'correo_usuario': corruser,
#             'correo_pswd': corrpswd,
#             'correo_tls': corrtls,
#             'correo_remitente': corrrmte,
#             'dias_presu_venc': pre_dias,
#             'dias_mant_venc': man_dias,
#             'dias_caja_venc': ven_dias,
#             'cant_dias_def_venc': dias_ven,
#             'cartera_dash1': car_das1,
#             'inicio_bisemana': ini_bise,
#         }
#         form = ConfiguracionSistemaForm(empresa, initial=inicial)
#     else:
#         form = ConfiguracionSistemaForm(empresa, request.POST, request.FILES)
#         if form.is_valid():
#             save_conf_param(request.user.profile.empresa, 'listprec', form.cleaned_data['listaprecio'].id)
#             save_conf_param(request.user.profile.empresa, 'usrmant', form.cleaned_data['usrmant'].id)
#             if form.cleaned_data['imagen'] is not None:
#                 empresa.logo = form.cleaned_data['imagen']
#                 empresa.save()
#             save_conf_param(request.user.profile.empresa, 'dvmant', form.cleaned_data['dias_venc_mant'])
#             save_conf_param(request.user.profile.empresa, 'txtins', form.cleaned_data['texto_instalacion'])
#             save_conf_param(request.user.profile.empresa, 'txtdeins', form.cleaned_data['texto_desinstalacion'])
#             save_conf_param(request.user.profile.empresa, 'resvcorr', form.cleaned_data['correo_reserva'])
#             save_conf_param(request.user.profile.empresa, 'corrhost', form.cleaned_data['correo_host'])
#             save_conf_param(request.user.profile.empresa, 'corrport', form.cleaned_data['correo_port'])
#             save_conf_param(request.user.profile.empresa, 'corruser', form.cleaned_data['correo_usuario'])
#             save_conf_param(request.user.profile.empresa, 'corrpswd', form.cleaned_data['correo_pswd'])
#             save_conf_param(request.user.profile.empresa, 'corrtls', form.cleaned_data['correo_tls'])
#             save_conf_param(request.user.profile.empresa, 'corrrmte', form.cleaned_data['correo_remitente'])
#             save_conf_param(request.user.profile.empresa, 'tar_elim', form.cleaned_data['eliminar_tareas'])
#             save_conf_param(request.user.profile.empresa, 'tar_dias', form.cleaned_data['dias_tareas_eliminar'])
#             save_conf_param(request.user.profile.empresa, 'pre_dias', form.cleaned_data['dias_presu_venc'])
#             save_conf_param(request.user.profile.empresa, 'man_dias', form.cleaned_data['dias_mant_venc'])
#             save_conf_param(request.user.profile.empresa, 'ven_dias', form.cleaned_data['dias_caja_venc'])
#             save_conf_param(request.user.profile.empresa, 'dias_ven', form.cleaned_data['cant_dias_def_venc'])
#             save_conf_param(request.user.profile.empresa, 'ini_bise', form.cleaned_data['inicio_bisemana'].strftime("%Y-%m-%d"))

#             # if form.cleaned_data['cartera_s1'] is not None:
#             #     save_conf_param(request.user.profile.empresa, 'car_s1', form.cleaned_data['cartera_s1'].id)
#             # if form.cleaned_data['cartera_s2'] is not None:
#             #     save_conf_param(request.user.profile.empresa, 'car_s2', form.cleaned_data['cartera_s2'].id)
#             save_conf_param(request.user.profile.empresa, 'comrecbo', form.cleaned_data['comprobante_recibo'].id)
#             save_conf_param(request.user.profile.empresa, 'carrecbo', form.cleaned_data['cartera_recibo'].id)
#             save_conf_param(request.user.profile.empresa, 'comcarec', form.cleaned_data['comprobante_caja_recibo'].id)
#             save_conf_param(request.user.profile.empresa, 'comvent', form.cleaned_data['comprobante_venta'].id)
#             save_conf_param(request.user.profile.empresa, 'car_das1', form.cleaned_data['cartera_dash1'].id)
#             save_conf_param(request.user.profile.empresa, 'mpdefau', form.cleaned_data['mpago_default'].id)
#             return redirect('/')
#         else:
#             print(form.errors)
#     context = {
#         'form': form,
#     }
#     return render(request, 'configuracion_sistema.html', context)


@login_required
def ajax_get_tarea_data(request):
    try:
        tarea_id = int(request.GET.get('tarea'))
        tarea = TareaUsuario.objects.get(id = tarea_id)
        obj_data = {
            key: value for key, value in tarea.__dict__.items() if isinstance(value, (int, str, bool, float, Decimal, datetime))
        }
        obj_data['tiempo'] = tiempo_transcurrido(tarea.timestamp)
        data = {'response': 0, 'data': obj_data}
    except:
        data = {'response': 1, 'data': None}
    return JsonResponse(data)





@login_required
def admin_mensajes_usuarios(request):
    if request.method == 'POST':
         mensajes_seleccionados = request.POST.getlist('delete')
         for mensaje_id in mensajes_seleccionados:
            try:
                msg = MensajeUsuario.objects.get(id=int(mensaje_id))
                msg.delete()
            except:
                return redirect('admin_mensajes_usuarios')
    
    
    fecha = timezone.now().strftime('%Y-%m-%d')
    mensajes = MensajeUsuario.objects.all()
    context = {
        'fecha' : fecha,
        'mensajes': mensajes,
    }
    return render(request, 'admin_mensajes_usuarios.html', context)


@login_required
def ajax_borrar_tarea(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tarea_id = data.get('codigo')
            tarea = TareaUsuario.objects.get(id = tarea_id)
            if tarea.ordenada_por == request.user:
                tarea.delete()
                response_data = {'response': 0, 'mensaje': 'alta OK'}
                return JsonResponse(response_data)
            else:
                return JsonResponse({'mensaje': 'No se permite borrar tareas no asignadas a si mismo'}, status=405)
        except:
            return JsonResponse({'mensaje': 'Error en tarea'}, status=405)    
    else:
        return JsonResponse({'mensaje': 'Metodo no permitido'}, status=405)
    


@login_required
def configuracion(request):
    if request.method == 'GET':
        inicial = {
            'nombre':request.user.first_name,
            'apellido':request.user.last_name,
            'email': request.user.email,
            'imagen':request.user.profile.image,
        }
        form = ConfiguracionForm(initial=inicial)
    else:
        form = ConfiguracionForm(request.POST, request.FILES)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['nombre']
            request.user.last_name = form.cleaned_data['apellido']
            request.user.email = form.cleaned_data['email']
            if form.cleaned_data['imagen'] is not None:
                request.user.profile.image = form.cleaned_data['imagen']
            request.user.save()
            return redirect('/')
        else:
            print(form.errors)
    context = {
        'form': form,
    }
    return render(request, 'configuracion_personal.html', context)


@login_required
def comprobantes(request):
    comprobantes = Comprobante.objects.filter(empresa = request.user.profile.empresa).order_by('descripcion')
    if request.method == 'POST':
        if request.POST.get('registro_id') != '':
            try:
                comprobante_id = int(request.POST.get('registro_id'))
                comprobante = Comprobante.objects.get(id = comprobante_id)
                form = ComprobanteABMForm(request.POST, instance = comprobante)
            except:
                return redirect('comprobantes')
        else:        
            form = ComprobanteABMForm(request.POST)
        if form.is_valid():
            if request.POST.get('eliminar'):
                comprobante.delete()
            else:
                comprob = form.save(commit=False)
                comprob.empresa = request.user.profile.empresa
                comprob.save()
            form = ComprobanteABMForm()            
    else:                
        form = ComprobanteABMForm()
    context = {
        'comprobantes':comprobantes,
        'form': form,
    }
    return render(request, 'comprobantes.html', context)

@login_required
def ajax_get_comprob_data(request):
    try:
        comprobante_id = int(request.GET.get('comprobante'))
        comprobante = Comprobante.objects.get(id = comprobante_id)
        obj_data = {
            key: value for key, value in comprobante.__dict__.items() if isinstance(value, (int, str, bool, float, Decimal))
        }
        data = {'response': 0, 'data': obj_data}
    except:
        data = {'response': 1, 'data': None}
    return JsonResponse(data)


@login_required
def carteras(request):
    carteras = Cartera.objects.filter(empresa = request.user.profile.empresa).order_by('nombre')
    if request.method == 'POST':
        if request.POST.get('registro_id') != '':
            try:
                cartera_id = int(request.POST.get('registro_id'))
                cartera = Cartera.objects.get(id = cartera_id)
                form = CarteraABMForm(request.POST, instance = cartera)
            except:
                return redirect('carteras')
        else:        
            form = CarteraABMForm(request.POST)
        if form.is_valid():
            if request.POST.get('eliminar'):
                cartera.delete()
            else:
                carte = form.save(commit=False)
                carte.empresa = request.user.profile.empresa
                carte.save()
            form = CarteraABMForm()            
    else:                
        form = CarteraABMForm()
    context = {
        'carteras':carteras,
        'form': form,
    }
    return render(request, 'carteras.html', context)


@login_required
def ajax_get_cart_data(request):
    try:
        cartera_id = int(request.GET.get('cartera'))
        cartera = Cartera.objects.get(id = cartera_id)
        habitacion_data = {
            key: value for key, value in cartera.__dict__.items() if isinstance(value, (int, str, bool, float, Decimal))
        }
        data = {'response': 0, 'data': habitacion_data}
    except:
        data = {'response': 1, 'data': None}
    return JsonResponse(data)

@login_required
@user_passes_test(es_staff)
def movimientos_caja(request):
    empresa = request.user.profile.empresa
    if not access_check(request.user, 'movimientos_caja'):
        return access_not_allowed(request)
    if request.method == 'GET':
        dias_ven = get_logic_param(empresa, 'dias_ven')
        if request.GET.get('fecha'):
            fecha = request.GET.get('fecha')
            fecha_hoy = datetime.strptime(fecha, '%Y-%m-%d').date()
        else:
            fecha_hoy = timezone.now().date()
            fecha = fecha_hoy.strftime('%Y-%m-%d')
        form = MovimientosCajaForm(empresa, initial = {'vencimiento': fecha_hoy  + timedelta(days=dias_ven)})
    else:
        form = MovimientosCajaForm(empresa, request.POST)
        if form.is_valid():
            caja_new = form.save(commit=False)
            comprobante_asociado = caja_new.comprobante
            if comprobante_asociado.numero is None:
                comprobante_asociado.numero = 1
            else:
                comprobante_asociado.numero += 1
            comprobante_asociado.save()
            caja_new.usuario = request.user
            hora_actual = timezone.localtime(timezone.now()).time()
            nueva_fecha = caja_new.fecha.replace(hour=hora_actual.hour, minute=hora_actual.minute, second=hora_actual.second)
            caja_new.fecha = nueva_fecha
            caja_new.empresa = request.user.profile.empresa
            caja_new.save()
            form = MovimientosCajaForm(request.user.profile.empresa)
        fecha_hoy = timezone.localtime(timezone.now()).date()
        fecha = fecha_hoy.strftime('%Y-%m-%d')
    context = {
        'fecha': fecha,
        'form': form,
    }
    return render(request, 'movimientos_caja.html', context)


@login_required
def ajax_load_saldos_cartera(request):
    cartera_id = request.GET.get('cartera')
    saldo = 0
    total_debe=0
    total_haber=0
    lista = []
    if cartera_id != '':
        cajas = Caja.objects.filter(cartera__id = cartera_id, empresa = request.user.profile.empresa).order_by('fecha')
        for caja in cajas:
            saldo += (ceronull(caja.debe) - ceronull(caja.haber))
            total_debe += ceronull(caja.debe)
            total_haber += ceronull(caja.haber)
            caja_data = {
                'fecha': caja.fecha.strftime('%d/%m/%Y - %H:%M:%S'),
                'comprobante': caja.comprobante.descripcion,
                'numero': caja.numero,
                'vencimiento': caja.vencimiento.strftime('%d/%m/%Y'),
                'descripcion': caja.descripcion[0:100],
                'debe':ceronull(caja.debe),
                'haber': ceronull(caja.haber),
                'saldo': saldo,
            }
            lista.append(caja_data)
    lista.append({
        'fecha': '',
        'comprobante': '',
        'numero': '',
        'descripcion': 'Total:',
        'debe':total_debe,
        'haber': total_haber,
        'saldo': saldo,

    })
    data = {'resultado': 0, 'data': lista}
    return JsonResponse(data)



@login_required
def ajax_comprobante_numero(request):
    com_id = request.GET.get('comprobante')
    try:
        com = Comprobante.objects.get(id = com_id)
        if com.automatico:
            data = {'resultado': 0, 'automatico': '1', 'numero': com.numero, 'signo': com.signo}
        else:
            data = {'resultado': 0, 'automatico': '0', 'signo': com.signo}
    except:
        data = {'resultado': 1}
    return JsonResponse(data)



@login_required
def cajaybanco_reportes(request):
    fecha = timezone.now().strftime('%Y-%m-%d')
    context = {
        'fecha' : fecha,
    }
    return render(request, 'cajaybanco_reportes.html', context)



@login_required
@user_passes_test(es_staff)
def abmAccesos(request):
    print('hola')
    accesos = AccesoPerfil.objects.filter(empresa = request.user.profile.empresa).order_by('rubroUsuario').order_by('pantalla')
    if request.method == 'POST':
        if request.POST.get('registro_id') != '':
            try:
                acceso_id = int(request.POST.get('registro_id'))
                acceso = AccesoPerfil.objects.get(id = acceso_id)
                form = AccesoABMForm(request.POST, instance = acceso)
            except:
                return redirect('abmAccesos')
        else:        
            form = AccesoABMForm(request.POST)
        if form.is_valid():
            if request.POST.get('eliminar'):
                acceso.delete()
            else:
                objeto = form.save(commit=False)
                objeto.empresa = request.user.profile.empresa
                objeto.save()
            form = AccesoABMForm()
    else:                
        form = AccesoABMForm()
    context = {
        'accesos':accesos,
        'form': form,
    }
    return render(request, 'abmAccesos.html', context)

@login_required
def ajax_get_obj_data(request):
    try:
        obj_id = int(request.GET.get('identifier'))
        aplicacion = request.GET.get('aplicacion')
        tabla = request.GET.get('tabla')
        try:
            Modelo = apps.get_model(aplicacion, tabla)
            obj = Modelo.objects.get(id = obj_id)
            obj_data = {
                key: value for key, value in obj.__dict__.items() if isinstance(value, (int, str, bool, float, Decimal))
            }
            data = {'response': 0, 'data': obj_data}
            print(obj_data)
        except:
            data = {'response': 2, 'data': None}
    except:
        data = {'response': 1, 'data': None}
    return JsonResponse(data)
