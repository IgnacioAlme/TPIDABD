from django.urls import path
from . import views

urlpatterns = [
    path('reservation/<str:id>', views.reserva_pasajes, name='hacer_reserva'),
    path('unit-status/<str:id>', views.mantenimiento_unidades, name='mantenimiento_unidades')
]
#     path('', views.reserva_pasajes, name='reserva_pasajes'),
#     
# ]