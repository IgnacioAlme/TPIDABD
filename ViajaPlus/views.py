#Cargar referencias a la DB
from .models import *

#Para conectar con la base de datos
from django.db import connection

#Formularios
from .forms import *

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
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
    context = {}
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
        parada_origen = tramo[0]
        parada_destino = tramo[1]
        
        #Invoca la funcion en el servidor SQL: Encargada de crear la reserva
        factura = invocar_funcion_postgresql('hacer_reserva',
                                   Perfil.objects.get(email=email_usuario).uid,
                                   id,
                                   parada_origen,
                                   parada_destino)
    return render(request, 'make_reservation.html', context)

def buscador_servicio(request):
    context = {}

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
            return render(request, 'search_for_service.html',context)

        return redirect('buscar_servicio', 'servicios', f'{localidad_origen.id_localidad}$&{localidad_destino.id_localidad}')

    return render(request, 'search_for_service.html',context)

# #El mantenimiento de los equipos requiere que el usuario tenga permiso administrador
# @login_required(login_url='login')
# @permission_required('authusuario.es_usuario_admin', raise_exception=True)
def mantenimiento_unidades(request, id):
    context = {}
    info_unidad = UnidadTransporte.objects.get(pk=int(id))

    if request.method == 'GET':
        context = {'form' : MantenimientoUnidadForm(instance=info_unidad), 'info_unidad' : info_unidad}
        
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

    return render(request, 'unit_management.html',context)

