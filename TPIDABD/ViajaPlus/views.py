#Cargar referencias a la DB
from .models import *

#Para conectar con la base de datos
from django.db import connection

#Formularios
from .forms import *

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Count
from django.http.response import Http404, HttpResponseRedirect
from datetime import datetime, date
from urllib.parse import unquote

#Funciones para las funciones de PotgreSQL cargadas
def invocar_funcion_postgresql(function_name:str, *args):
    with connection.cursor() as cursor:
        #Ejecuta la funcion
        cursor.execute(f"SELECT {function_name}{str(args)}")
        #Obtener los resultados
        resultados = cursor.fetchall()
        return resultados

#Funcion para convertir el texto de localidad en el formato para nombres
def acondicionar_localidad(texto:str):
    texto = texto.lower()
    palabras = texto.split(" ")
    resultado = ''
    for p in palabras:
        resultado += p[0].upper()+p[1:len(p)]
    return resultado

#Funcion para calcular costo
def get_costo(costo_base:float, diferencial_precio:float, categoria_transporte:str, atencion_servicio:str, descuento:float, delta_time:float):
    #Valores que aumentan el precio
    multiplicador = 1
    match categoria_transporte:
        case 'comun':
            multiplicador += 0
        case 'semicama':
            multiplicador += 0.25
        case 'cochecama':
            multiplicador += 0.5
    match atencion_servicio:
        case 'comun':
            multiplicador += 0
        case 'ejecutivo':
            multiplicador += 0.5
    #aplicar el descuento al multiplicador (de 0 a 1)
    multiplicador *= (1 - descuento)
    #devolver el costo de la ecuación
    return diferencial_precio*multiplicador*delta_time + costo_base

#Buscador de servicos
def buscar_info(request, operation, info = ""):
    context = {}
    info_web = {'es_servicio':False,
                'titulo':'TITULO'
                }
    match operation:
        case 'servicios':
            info_web['es_servicio'] = True
            if info == "":
                info_web['filtered'] = False
                resultados = Servicio.objects.all().order_by("pk")
                info_del_servicio = resultados
            else:
                info_web['filtered'] = True
                tramo = info.split('$&')
                lista_servicios = invocar_funcion_postgresql(
                    'get_tramo',
                    tramo[0],
                    tramo[1])
                
                info_del_servicio = {}
                if len(lista_servicios)>0:
                    for r in lista_servicios:
                       r = str(r[0][1:-1]).split(",")
                       info_del_servicio[int(r[0])] = [int(r[1]), int(r[2])]
                resultados = Servicio.objects.filter(pk__in = [j for j in info_del_servicio.keys()]).order_by("pk")
                #Devolver el servicio con el tramo de paradas a reservar
                resultados = zip(resultados, dict(sorted(info_del_servicio.items())).values())
            info_web['titulo'] = 'Lista de servicios'
        case 'unidades':
            resultados = UnidadTransporte.objects.all().order_by("pk")
            info_web['titulo'] = 'Lista de unidades'
    context = {'data' : resultados , 'info_web':info_web}
    return render(request, 'search_db.html', context)

#Operación de reserva de pasajes
#@login_required(login_url='login')
def reserva_pasajes(request, id, tramo):
    context = {'is_error':False}

    #Cargar el servicio y los tramos de paradas
    servicio = Servicio.objects.get(pk=int(id))
    if tramo == "all":
        paradas = Parada.objects.filter(id_itinerario = servicio.id_itinerario).order_by('pk')
        #Cargar las paradas
        parada_1 = paradas.first()
        parada_2 = paradas.last()
    else:
        #Cargar los tramos de la URL
        tramo = [int(i) for i in str(unquote(tramo)[1:-1]).split(",")]
        paradas = Parada.objects.filter(id_itinerario = servicio.id_itinerario).order_by('pk')
        #Cargar las paradas
        parada_1 = paradas.get(nro_parada=tramo[0])
        parada_2 = paradas.get(nro_parada=tramo[1])

    #Llamar la funcion del postgresql para obtener un asiento disponible
    id_asiento_disponible = invocar_funcion_postgresql(
        'get_asientos_disponibles_funciona_de_verdad',
        id,
        parada_1.nro_parada,
        parada_2.nro_parada
    )[0][0]

    #Y sus tiempos
    t_origen = parada_1.tiempo_llegada
    t_destino = parada_2.tiempo_llegada
    #Obtener las reservas que se hayan hecho en este servicio
    reservas_existentes = Reserva.objects.filter(id_servicio=servicio)
    asientos_reservados = AsientoReservado.objects.filter(id_reserva__in = reservas_existentes)
    sin_reservacion = Disposicion.objects.filter(id_unidad = servicio.id_unidad).exclude(id_disposicion__in = asientos_reservados)
    #Y las disposiciones de la unidad que emplee el servicio
    asientos_disponibles = None
    #Si no existen reservas asignar cualquier asiento
    print(sin_reservacion)
    if not sin_reservacion:
        asientos_disponibles = sin_reservacion.first()
    else:
        #si hay reservas, verificar que los tiempos de ocupación no se superpongan con el tramo
        for r in asientos_reservados:
            r = r.id_reserva
            _parada_destino = Parada.objects.get(pk = r.parada_destino, id_itinerario=servicio.id_itinerario)
            _parada_origen = Parada.objects.get(pk = r.parada_origen, id_itinerario=servicio.id_itinerario)
            if (_parada_destino.tiempo_llegada <= t_origen) or (_parada_origen.tiempo_llegada >= t_destino):
                asientos_disponibles = AsientoReservado.objects.get(id_reserva = r).id_disposicion
                break
    #Si no hay asientos disponibles alzar error
    if not asientos_disponibles:
        messages.add_message(request, messages.ERROR, 'Este servicio no cuenta con asientos disponibles para el tramo escogido')
        context['is_error'] = True
        return render(request, 'make_reservation.html', context)
    #Cargar las localidades que correspondan
    _first = parada_1.id_localidad
    _last = parada_2.id_localidad

    context = {'data':servicio.id_servicio,
                'date_from':servicio.fecha_partida + parada_1.tiempo_llegada, #datetime.timedelta(days=2)
                'place_from':f'{_first.nombre_terminal} de {_first.nombre}, {_first.provincia}',
                'place_to':f'{_last.nombre_terminal} de {_last.nombre}, {_last.provincia}',
                'date_to':servicio.fecha_llegada + parada_2.tiempo_llegada
    }

    if request.method == 'GET':
        context['form'] = HacerReservacion()
    if request.method == 'POST':
        form = HacerReservacion(request.POST) #Carga los campos con los Tag de la pagina HTML
        context['form'] = form
        if form.is_valid():
            form=form.clean()
        # Obtener los datos del formulario
        email_usuario = form['email_usuario']
        parada_origen = parada_1.nro_parada
        parada_destino = parada_2.nro_parada
        
        #Invoca la funcion en el servidor SQL: Encargada de crear la reserva
        id_reserva = invocar_funcion_postgresql('hacer_reserva_devuelve',
                                   Perfil.objects.get(email=email_usuario).uid,
                                   id,
                                   parada_origen,
                                   parada_destino)[0][0]
        id_reserva = Reserva.objects.get(pk=id_reserva)
        #Crear el Asiento_reservado
        asiento = AsientoReservado(
            id_reserva = id_reserva,
            id_disposicion = asientos_disponibles
        )
        asiento.save()
        #Crea el pasaje
        pasaje = Pasaje(
            id_reserva = id_reserva,
            costo = get_costo(
                servicio.id_itinerario.costo_base,
                servicio.diferencial_precio,
                servicio.id_unidad.categoria,
                servicio.atencion,
                id_reserva.descuento,
                (parada_2.tiempo_llegada - parada_1.tiempo_llegada).total_seconds()/3600
                )
            ) #TODO
        pasaje.save()
        
    return render(request, 'make_reservation.html', context)

def buscador_servicio(request):
    context = {}
    raise_error = False
    if request.method == 'GET':
        context = {'form' : BuscadorServicio()}
        
    elif request.method == 'POST':
        #obtener los datos del formulario
        form = BuscadorServicio(request.POST) #Carga los campos con los Tag de la pagina HTML
        context['form'] = form
        if form.is_valid():
            form=form.clean()

        #Y las variables
        localidad_origen = acondicionar_localidad(form['localidad_origen'])
        localidad_destino = acondicionar_localidad(form['localidad_destino'])

        #Verificar que las localidades estén en la base de datos
        try:
            localidad_origen = Localidad.objects.get(nombre=localidad_origen)
            localidad_destino = Localidad.objects.get(nombre=localidad_destino)
        except:
            messages.add_message(request, messages.ERROR, 'No se han encontrado servicios por esas localidades.')
            raise_error = True
        if not raise_error:
            return redirect('buscar_servicio', 'servicios', f'{localidad_origen.id_localidad}$&{localidad_destino.id_localidad}')

    return render(request, 'search_for_service.html',context)

# #El mantenimiento de los equipos requiere que el usuario tenga permiso administrador
# @login_required(login_url='login')
# @permission_required('authusuario.es_usuario_admin', raise_exception=True)
def mantenimiento_unidades(request, id):
    context = {}
    info_unidad = UnidadTransporte.objects.get(pk=int(id))

    if request.method == 'GET':
        context = {'title':'Gestión de unidades', 'form' : MantenimientoUnidadForm(instance=info_unidad), 'info' : info_unidad}
        
    elif request.method == 'POST':
        #obtener los datos del formulario
        form = MantenimientoUnidadForm(request.POST) #Carga los campos con los Tag de la pagina HTML
        context['form'] = form
        if form.is_valid():
            form=form.clean()
        
        #Actualizar la unidad
        info_unidad.cant_pisos = form['cant_pisos']
        info_unidad.categoria = form['categoria']
        info_unidad.patente = form['patente']
        info_unidad.disponibilidad = bool(form['disponibilidad'])
        info_unidad.save()

    return render(request, 'admin_form.html',context)

def admin_servicio(request, id=''):
    context = {'view_list':False}
    if id == '':
        info_servicio = Servicio.objects.all().order_by("pk")
        context["data"] = info_servicio
        context['view_list'] = True
        return render(request, 'admin_form.html',context) 

    info_servicio = Servicio.objects.get(pk=int(id))

    if request.method == 'GET':
        context = {'title':'Gestión de servicio', 'form' : AdministrarServicioForm(instance=info_servicio), 'info' : info_servicio}
        
    elif request.method == 'POST':
        #obtener los datos del formulario
        form = AdministrarServicioForm(request.POST) #Carga los campos con los Tag de la pagina HTML
        context['form'] = form
        if form.is_valid():
            form=form.clean()
        
        #Actualizar la unidad
        info_servicio.atencion = form['atencion']
        info_servicio.fecha_partida = form['fecha_partida']
        info_servicio.fecha_llegada = form['fecha_llegada']
        info_servicio.disponibilidad = form['disponibilidad']
        info_servicio.diferencial_precio = form['diferencial_precio']
        info_servicio.creador = form['creador']
        info_servicio.id_itinerario = form['id_itinerario']
        info_servicio.id_unidad = form['id_unidad']
        info_servicio.save()

    return render(request, 'admin_form.html',context)

def ver_estadisticas(request):
    context = {}
    reservas = Reserva.objects.all()

    #Dar datos para la página
    context['data'] = reservas.order_by('-fecha_creacion')
    context['data_itinerario'] = reservas.values('id_itinerario').annotate(cantidad=Count('id_itinerario')).order_by()
    context['data_time'] = reservas.values("fecha_creacion__date").annotate(cantidad=Count('fecha_creacion__date'),antidad_pendiente=Count('estado')).order_by('-fecha_creacion__date')

    return render(request, 'statistics_reservations.html', context)