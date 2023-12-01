from django.db import models

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

class CantPisos(models.Choices):
    UNO = 1
    DOS = 2

class Perfil(models.Model):
    uid = models.UUIDField(primary_key=True)
    email = models.CharField(unique=True)
    nombre = models.CharField()
    apellido = models.CharField()
    fecha_nacimiento = models.DateTimeField(blank=True, null=True)
    rol = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'perfil'
        db_table_comment = 'Datos de usuarios'

#Modelos de la base de datos
class Localidad(models.Model):
    id_localidad = models.AutoField(auto_created=True, primary_key=True)
    pais = models.CharField(max_length=20)
    provincia = models.CharField(max_length=80)
    nombre = models.CharField(max_length=20)
    nombre_terminal = models.CharField(max_length=80)

    class Meta:
        managed = False
        db_table = 'localidad'
        db_table_comment = 'Localidades'

class Itinerario(models.Model):
    id_itinerario = models.AutoField(auto_created=True, primary_key=True,db_column='id')
    hora_partida = models.TimeField()
    costo_base = models.FloatField()

    class Meta:
        managed = False
        db_table = 'itinerario'


class UnidadTransporte(models.Model):
    id_unidad = models.BigAutoField(auto_created=True, primary_key=True)
    cant_pisos = models.IntegerField(choices=CantPisos.choices, default=CantPisos.UNO)
    categoria = models.CharField(choices=Categoria.choices, default=Categoria.COMUN)
    patente = models.CharField(max_length=8, blank=True, null=True)
    disponibilidad = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'unidad_transporte'

class Parada(models.Model):
    nro_parada = models.AutoField(auto_created=True, primary_key=True)
    id_itinerario = models.ForeignKey(Itinerario, on_delete=models.CASCADE)
    tiempo_llegada = models.DurationField()
    id_localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'parada'
        unique_together = (('nro_parada', 'id_itinerario'),)

class Servicio(models.Model):
    id_servicio = models.AutoField(auto_created=True, primary_key=True)
    atencion = models.CharField(max_length=30, choices=Atencion.choices, default=Atencion.COMUN)
    fecha_partida = models.DateField()
    fecha_llegada = models.DateField()
    disponibilidad = models.IntegerField()
    diferencial_precio = models.FloatField()
    creador = models.ForeignKey(Perfil, on_delete=models.CASCADE, db_column='creador', blank=True, null=True)
    id_itinerario = models.ForeignKey(Itinerario, on_delete=models.CASCADE, db_column='id_itinerario')
    id_unidad = models.ForeignKey('UnidadTransporte', on_delete=models.CASCADE, db_column='id_unidad')

    class Meta:
        managed = False
        db_table = 'servicio'

class Disposicion(models.Model):
    id_unidad = models.OneToOneField('UnidadTransporte', on_delete=models.CASCADE, db_column='id_unidad', primary_key=True)
    fila = models.IntegerField()
    hilera = models.IntegerField()
    piso = models.IntegerField() #TODO: cambiar cant_pisos a Int en la base de datos

    class Meta:
        managed = False
        db_table = 'disposicion'
        unique_together = (('id_unidad', 'fila', 'hilera', 'piso'),)
        db_table_comment = 'Disposicion de los asientos en una unidad de transporte'

class Reserva(models.Model):
    id_reserva = models.AutoField(auto_created=True, primary_key=True)
    id_cliente = models.ForeignKey(Perfil, on_delete=models.CASCADE, db_column='id_cliente')
    id_servicio = models.ForeignKey('Servicio', on_delete=models.CASCADE, db_column='id_servicio')
    id_itinerario=models.ForeignKey(Itinerario, on_delete=models.CASCADE, db_column='id_itinerario', to_field='id_itinerario')
    parada_origen = models.BigIntegerField()
    parada_destino = models.BigIntegerField()
    fecha_creación = models.DateTimeField(auto_now_add=True, editable=False)
    fecha_pago = models.DateTimeField()
    descuento = models.FloatField()
    estado = models.CharField(max_length=30, choices=Estado.choices, default=Estado.PENDIENTE)

    class Meta:
        managed = False
        db_table = 'reserva'

class Pasaje(models.Model):
    id_pasaje = models.AutoField(auto_created=True, primary_key=True)
    id_reserva = models.ForeignKey('Reserva', models.DO_NOTHING, db_column='id_reserva')
    costo = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pasaje'

class AsientoReservado(models.Model):
    id_reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, db_column='id_reserva', primary_key=True)
    id_unidad = models.ForeignKey('Disposicion', on_delete=models.CASCADE, db_column='id_unidad')
    piso = models.IntegerField()  # This field type is a guess.
    fila = models.SmallIntegerField()
    hilera = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'asientos_reservados'
        unique_together = (('id_reserva', 'id_unidad', 'piso', 'fila', 'hilera'),)
