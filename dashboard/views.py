from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from datetime import date, timedelta
import json
from espacios.models import Espacio, TipoEspacio
from reservas.models import Reserva
from django.contrib.auth.models import User
from .reportes import generar_pdf_reservas, generar_excel_reservas, filtrar_reservas
from usuarios.decorators import rol_requerido


@login_required
def dashboard_inicio(request):
    """
    Vista principal del dashboard.
    Muestra KPIs, gráficos y actividad reciente.
    Para usuarios normales muestra sus próximas reservas.
    Para admin/operador muestra datos globales.
    """
    hoy = date.today()
    hace_30 = hoy - timedelta(days=30)
    
    # ─── KPIs (Indicadores clave) ───
    total_espacios = Espacio.objects.count()
    total_reservas = Reserva.objects.count()
    reservas_hoy = Reserva.objects.filter(fecha=hoy).count()
    reservas_pendientes = Reserva.objects.filter(estado='pendiente').count()
    
    # ─── Reservas del usuario actual ───
    # Si es admin/operador no mostramos "mis reservas" (ya ven todo)
    if request.user.perfil.rol not in ['admin', 'operador']:
        mis_reservas = Reserva.objects.filter(
            usuario=request.user,
            fecha__gte=hoy  # Solo reservas futuras o de hoy
        ).select_related('espacio').order_by('fecha', 'hora_inicio')[:5]
    else:
        mis_reservas = None
    
    # ─── GRÁFICO 1: Reservas por mes (últimos 6 meses) ───
    reservas_mes = (
        Reserva.objects
        .filter(fecha__gte=hoy - timedelta(days=180))  # Últimos 180 días ≈ 6 meses
        .annotate(mes=TruncMonth('fecha'))              # Agrupar por mes
        .values('mes')
        .annotate(total=Count('id'))                    # Contar reservas por mes
        .order_by('mes')
    )
    labels_meses = [r['mes'].strftime('%b %Y') for r in reservas_mes]
    data_meses = [r['total'] for r in reservas_mes]
    
    # ─── GRÁFICO 2: Top 5 espacios más usados ───
    top_espacios = (
        Espacio.objects
        .annotate(num=Count('reservas'))  # Cuenta las reservas de cada espacio
        .order_by('-num')[:5]             # Los 5 con más reservas
    )
    labels_top = [e.nombre[:25] for e in top_espacios]  # Truncar nombres largos
    data_top = [e.num for e in top_espacios]
    
    # ─── GRÁFICO 3: Distribución por tipo de espacio ───
    tipos = TipoEspacio.objects.annotate(
        num=Count('espacios__reservas')  # Reservas de espacios de cada tipo
    ).filter(num__gt=0)                   # Solo tipos con al menos 1 reserva
    
    labels_tipos = [t.nombre for t in tipos]
    data_tipos = [t.num for t in tipos]
    
    # ─── GRÁFICO 4: Ocupación semanal ───
    inicio_sem = hoy - timedelta(days=hoy.weekday())  # Lunes de esta semana
    dias_nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    data_semana = []
    for i in range(7):
        d = inicio_sem + timedelta(days=i)
        count = Reserva.objects.filter(fecha=d, estado='confirmada').count()
        data_semana.append(count)
    
    # ─── Actividad reciente ───
    actividad_reciente = Reserva.objects.select_related(
        'usuario', 'espacio'
    ).order_by('-creada_en')[:10]  # Últimas 10 reservas creadas
    
    # ─── Pasamos todo al template ───
    context = {
        # KPIs
        'total_espacios': total_espacios,
        'total_reservas': total_reservas,
        'reservas_hoy': reservas_hoy,
        'reservas_pendientes': reservas_pendientes,
        'mis_reservas': mis_reservas,
        
        # Gráfico 1
        'labels_meses': json.dumps(labels_meses),
        'data_meses': json.dumps(data_meses),
        
        # Gráfico 2
        'labels_top': json.dumps(labels_top),
        'data_top': json.dumps(data_top),
        
        # Gráfico 3
        'labels_tipos': json.dumps(labels_tipos),
        'data_tipos': json.dumps(data_tipos),
        
        # Gráfico 4
        'labels_dias': json.dumps(dias_nombres),
        'data_semana': json.dumps(data_semana),
        
        # Actividad
        'actividad_reciente': actividad_reciente,
    }
    
    return render(request, 'dashboard/inicio.html', context)


@login_required
@rol_requerido('admin')  # Solo administradores pueden ver reportes
def reportes(request):
    """
    Página de reportes con filtros para descargar PDF/Excel.
    Muestra tabla previa de reservas filtradas antes de descargar.
    Solo accesible por admin.
    """
    fecha_inicio = request.GET.get('inicio')
    fecha_fin = request.GET.get('fin')
    
    # Obtener reservas filtradas (si se enviaron fechas, si no, todas)
    reservas = filtrar_reservas(fecha_inicio, fecha_fin)
    
    context = {
        'reservas': reservas,
        'total_reservas': reservas.count(),
        'fecha_inicio': fecha_inicio or '',
        'fecha_fin': fecha_fin or '',
    }
    return render(request, 'dashboard/reportes.html', context)


@login_required
@rol_requerido('admin')
def descargar_pdf(request):
    """
    Vista que genera y descarga el reporte en PDF.
    Recibe parámetros GET: inicio (fecha) y fin (fecha).
    """
    fecha_inicio = request.GET.get('inicio')
    fecha_fin = request.GET.get('fin')
    return generar_pdf_reservas(fecha_inicio, fecha_fin)


@login_required
@rol_requerido('admin')
def descargar_excel(request):
    """
    Vista que genera y descarga el reporte en Excel.
    Recibe parámetros GET: inicio (fecha) y fin (fecha).
    """
    fecha_inicio = request.GET.get('inicio')
    fecha_fin = request.GET.get('fin')
    return generar_excel_reservas(fecha_inicio, fecha_fin)