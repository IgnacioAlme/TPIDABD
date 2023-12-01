#Cargar referencias a la DB
from django.contrib.auth.models import User
from authusuario.models import Perfil
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

#Operación de reserva de pasajes
@login_required(login_url='login')
def reserva_pasajes(request, id_servicio):
    context = {'is_error' : False}
    if request.method == 'GET':
        context = {'form' : HacerReservacion()}
    if request.method == 'POST':
        form = HacerReservacion(request.POST) #Carga los campos con los Tag de la pagina HTML
        context['form'] = form
        if form.is_valid():
            form=form.clean()
        # Obtener los datos del formulario
        parada_origen = form['parada_origen']
        parada_destino = form['parada_destino']
        
        #Invoca la funcion en el servidor SQL: Encargada de crear la reserva
        factura = invocar_funcion_postgresql('hacer_reserva',
                                   Perfil.objects.get(username=request.user.username).uid,
                                   id_servicio,
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

