import uuid #para generar uid para los usuarios
from django.db import models
from django.contrib.auth.models import User

#models.User tiene los datos --> se usará para llamar únicamente 'User' correspondiente al auth.user.id
    #User
    #username
    #first_name
    #last_name
    #email
    #password
    #groups
    #user_permisions
    #is_staff
    #is_active
    #is_superuser
    #last_login
    #date_joined

class Permisos(models.Model):
    class Meta:
        permissions = [
            ("es_usuario_admin", "Acceso a herramientas del sitio")
        ]

#Para manejar la base de datos en postgresql
class Roles(models.TextChoices): #TODO: Cargar los roles que puede tener el usuario
    CLIENTE='Cliente'
    CONDUCTOR='Conductor'
    ADMIN='Admin'

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email=models.CharField(max_length=50, default= "email@email.com")
    nombre=models.CharField(max_length=50, default= "Nombre")
    apellido=models.CharField(max_length=50, default= "Apellido")
    fecha_nacimiento=models.DateField()
    rol=models.CharField(max_length=30, choices=Roles.choices, default=Roles.CLIENTE)