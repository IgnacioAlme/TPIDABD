from django import forms
from .models import UnidadTransporte, AsientoReservado, Disposicion

Opciones_Atencion = (
    ("Común", "Común"),
    ("Ejecutivo", "Ejecutivo")
)
Opciones_Estado = (
    ("Pendiente", "Pendiente"),
    ("Cancelado", "Cancelado"),
    ("Pagado", "Pagado")
)

#Campos requeridos por el formulario html para realizar una reservación
class HacerReservacion(forms.Form):
    email_usuario = forms.CharField(required=True)

#Campos para definir el estado de una unidad de transporte
class MantenimientoUnidadForm(forms.ModelForm):
    class Meta:
        model = UnidadTransporte
        fields = ("cant_pisos","categoria","patente","disponibilidad")

#Para busqueda de servicios
class BuscadorServicio(forms.Form):
    localidad_origen = forms.CharField(max_length=38, required=True)
    localidad_destino = forms.CharField(max_length=38, required=True)

