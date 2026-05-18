from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    path('', views.lista_reservas, name='lista'),
    path('crear/', views.crear_reserva, name='crear'),
    path('calendario/', views.calendario_reservas, name='calendario'),
    path('<int:pk>/', views.detalle_reserva, name='detalle'),
    path('<int:pk>/editar/', views.editar_reserva, name='editar'),
    path('<int:pk>/cancelar/', views.cancelar_reserva, name='cancelar'),
    path('<int:pk>/confirmar/', views.confirmar_reserva, name='confirmar'),
]