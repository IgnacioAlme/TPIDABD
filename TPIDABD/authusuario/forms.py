from django import forms
from .models import Perfil, Roles

#Campos requeridos por el formulario html para crear un usuario
class new_profile(forms.Form):
    email=forms.CharField(max_length=50, label='Email', required=True)
    nombre=forms.CharField(max_length=50, label='Nombre', required=True)
    apellido=forms.CharField(max_length=50, label='Apellido', required=True)
    fecha_nacimiento=forms.DateField(label='Fecha de nacimiento', required=True)
    rol=forms.CharField(max_length=30, label='Rol', choices=Roles.choices, default=Roles.PASAJERO, required=True)
    password = forms.CharField(max_length=50, label='Contraseña', required=True)
    repeat_password = forms.CharField(max_length=50, label='Repetir contraseña', required=True)
