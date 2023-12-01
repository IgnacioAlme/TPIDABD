from django.db import models
from authusuario.models import Perfil
from enum import Enum

#Referencias y categorías
class Categoria(models.TextChoices):
    COMUN = 'comun'
    SEMICAMA = 'semicama'
    COCHECAMA = 'cochecama'

class Atencion(models.TextChoices):
    COMUN = 'comun'
    EJECUTIVO = 'ejecutivo'

class Estado(models.TextChoices):
    PENDIENTE = 'pendiente'
    CANCELADO = 'cancelada'
    PAGADO = 'pagada'

class CantPisos(models.TextChoices):
    UNO = "uno"
    DOS = "dos"

#Modelos de la base de datos
# class Localidad(models.Model):
#     id_localidad = models.AutoField(auto_created=True, primary_key=True)
#     pais = models.CharField(max_length=20)
#     provincia = models.CharField(max_length=80)
#     nombre = models.CharField(max_length=20)
#     nombre_terminal = models.CharField(max_length=80)

class Intinerario(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    hora_partida = models.TimeField()
    costo_base = models.FloatField()

    class Meta:
        managed = False
        db_table = 'itinerario'


class UnidadTransporte(models.Model):
    id_unidad = models.BigAutoField(auto_created=True, primary_key=True)
    cant_pisos = models.CharField(choices=CantPisos.choices, default=CantPisos.UNO)
    categoria = models.CharField(choices=Categoria.choices, default=Categoria.COMUN)
    patente = models.CharField(max_length=8, blank=True, null=True)
    disponibilidad = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'unidad_transporte'

# class Parada(models.Model):
#     nro_parada = models.AutoField(auto_created=True, primary_key=True)
#     id_intinerario = models.ForeignKey(Intinerario, on_delete=models.CASCADE)
#     tiempo_llegada = models.TimeField() #TODO: se refiere a fecha y hora de llegada?
#     id_localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE)

# class Servicio(models.Model):
#     id_servicio = models.AutoField(auto_created=True, primary_key=True)
#     atencion = models.CharField(max_length=30, choices=Atencion.choices, default=Atencion.COMUN)
#     fecha_partida = models.DateTimeField()
#     fecha_llegada = models.DateTimeField()
#     disponibilidad = models.IntegerField(max_length=8)
#     diferencial_precio = models.FloatField()
#     creador = models.ForeignKey(Perfil, on_delete=models.CASCADE)
#     id_intinerario = models.ForeignKey(Intinerario, on_delete=models.CASCADE)
#     id_unidad = models.ForeignKey(UnidadTransporte, on_delete=models.CASCADE)

# class Disposicion(models.Model):
#     id_unidad = models.ForeignKey(UnidadTransporte, on_delete=models.CASCADE, primary_key=True)
#     fila = models.IntegerField(max_length=2)
#     hilera = models.IntegerField(max_length=2)
#     piso = models.IntegerField(max_length=2) #TODO: cambiar cant_pisos a Int en la base de datos

# class Reserva(models.Model):
#     id_reserva = models.AutoField(auto_created=True, primary_key=True)
#     id_cliente = models.ForeignKey(Perfil, on_delete=models.CASCADE)
#     id_servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
#     id_intinerario=models.ForeignKey(Intinerario, on_delete=models.CASCADE)
#     parada_origen = models.ForeignKey(Parada, on_delete=models.CASCADE)
#     parada_destino = models.ForeignKey(Parada, on_delete=models.CASCADE)
#     fecha_creación = models.DateTimeField(auto_now_add=True, editable=False)
#     fecha_pago = models.DateTimeField()
#     descuento = models.FloatField()
#     estado = models.CharField(max_length=30, choices=Estado.choices, default=Estado.PENDIENTE)

# class Pasaje(models.Model):
#     id_pasaje = models.AutoField(auto_created=True, primary_key=True)
#     id_reserva = models.IntegerField(max_length=8)
#     costo = models.FloatField()

# class AsientoReservado(models.Model):
#     id_reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
#     id_reserva = models.ForeignKey(Disposicion, on_delete=models.CASCADE)
