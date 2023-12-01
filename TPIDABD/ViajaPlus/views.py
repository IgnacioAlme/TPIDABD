#Cargar referencias a la DB
from .models import *

#Para conectar con la base de datos
from django.db import connection

#Formularios
from .forms import *

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http.response import Http404, HttpResponseRedirect
from datetime import datetime, date

#Funciones para las funciones de PotgreSQL cargadas
def invocar_funcion_postgresql(function_name:str, *args):
    with connection.cursor() as cursor:
        #Ejecuta la funcion
        cursor.execute(f"SELECT {function_name}{str(args)}")
        #Obtener los resultados
        resultados = cursor.fetchall()
        return resultados

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
                resultados = Servicio.objects.all().order_by("pk")
                info_del_servicio = resultados
            else:
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
                print(info_del_servicio)
                resultados = Servicio.objects.filter(pk__in = [j for j in info_del_servicio.keys()]).order_by("pk")
            #resultados = zip(resultados, dict(sorted(info_del_servicio.items())))
            info_web['titulo'] = 'Lista de servicios'
        case 'unidades':
            resultados = UnidadTransporte.objects.all().order_by("pk")
            info_web['titulo'] = 'Lista de unidades'
    context = {'data' : resultados , 'info_web':info_web}
    return render(request, 'search_db.html', context)

#Operación de reserva de pasajes
#@login_required(login_url='login')
def reserva_pasajes(request, id, tramo):
    servicio = Servicio.objects.get(pk=int(id))
    context = {'data':{
        'id':servicio.pk,
        'desde':'',
        'hasta':''}}
    if request.method == 'GET':
        context = {'form' : HacerReservacion()}
    if request.method == 'POST':
        form = HacerReservacion(request.POST) #Carga los campos con los Tag de la pagina HTML
        context['form'] = form
        if form.is_valid():
            form=form.clean()
        # Obtener los datos del formulario
        email_usuario = form['email_usuario']
        parada_origen = form['parada_origen']
        parada_destino = form['parada_destino']
        
        #Invoca la funcion en el servidor SQL: Encargada de crear la reserva
        factura = invocar_funcion_postgresql('hacer_reserva',
                                   Perfil.objects.get(email=email_usuario).uid,
                                   id,
                                   parada_origen,
                                   parada_destino)
        
    return render(request, 'make_reservation.html', context)

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

