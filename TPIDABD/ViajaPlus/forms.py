from django import forms
from .models import UnidadTransporte

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
    parada_origen = forms.IntegerField(required=True)
    parada_destino = forms.IntegerField(required=True)


#Campos para definir el estado de una unidad de transporte
class MantenimientoUnidadForm(forms.ModelForm):
    class Meta:
        model = UnidadTransporte
        fields = ("cant_pisos","categoria","patente","disponibilidad")