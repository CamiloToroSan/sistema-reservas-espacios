from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_inicio, name='inicio'),
    
    # Página de reportes (solo admin)
    path('reportes/', views.reportes, name='reportes'),
    
    # Descarga de reportes
    path('reportes/pdf/', views.descargar_pdf, name='descargar_pdf'),
    path('reportes/excel/', views.descargar_excel, name='descargar_excel'),
]