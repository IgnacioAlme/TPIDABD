from django.urls import path
from . import views

urlpatterns = [
    path('ver/<str:operation>/', views.buscar_info, name='buscar_servicio'),
    path('ver/<str:operation>/<str:info>', views.buscar_info, name='buscar_servicio'),
    path('reservation/<str:id>/<str:tramo>', views.reserva_pasajes, name='hacer_reserva'),
    path('unit-status/<str:id>', views.mantenimiento_unidades, name='mantenimiento_unidades')
]
#     path('', views.reserva_pasajes, name='reserva_pasajes'),
#     
# ]?level=<int:cant>&temas=<str:temas>