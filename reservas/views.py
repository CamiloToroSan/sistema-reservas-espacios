from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import date, timedelta
from .models import Reserva, HistorialReserva
from .forms import ReservaForm
from .utils import enviar_confirmacion_reserva
from usuarios.decorators import rol_requerido


@login_required
def lista_reservas(request):
    if request.user.perfil.rol in ['admin', 'operador']:
        reservas = Reserva.objects.all()
    else:
        reservas = Reserva.objects.filter(usuario=request.user)
    
    reservas = reservas.select_related('espacio', 'usuario')
    
    # Filtros
    estado = request.GET.get('estado')
    if estado:
        reservas = reservas.filter(estado=estado)
    
    busqueda = request.GET.get('q', '').strip()
    if busqueda:
        reservas = reservas.filter(
            Q(motivo__icontains=busqueda) |
            Q(espacio__nombre__icontains=busqueda) |
            Q(usuario__username__icontains=busqueda)
        )
    
    return render(request, 'reservas/lista.html', {
        'reservas': reservas,
        'estado_seleccionado': estado or '',
        'busqueda': busqueda,
    })


@login_required
def detalle_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    
    # Solo el dueño, admin u operador pueden ver
    if reserva.usuario != request.user and request.user.perfil.rol not in ['admin', 'operador']:
        messages.error(request, 'No tienes permisos para ver esta reserva.')
        return redirect('reservas:lista')
    
    historial = reserva.historial.select_related('usuario').all()
    
    return render(request, 'reservas/detalle.html', {
        'reserva': reserva,
        'historial': historial,
    })


@login_required
def crear_reserva(request):
    espacio_id = request.GET.get('espacio')
    
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            
            # Si es admin u operador, confirma automáticamente
            if request.user.perfil.rol in ['admin', 'operador']:
                reserva.estado = 'confirmada'
            else:
                reserva.estado = 'pendiente'
            
            reserva.save()
            
            HistorialReserva.objects.create(
                reserva=reserva,
                usuario=request.user,
                accion='creada',
                comentario=f'Reserva creada por {request.user.username}'
            )
            
            try:
                enviar_confirmacion_reserva(reserva)
            except Exception as e:
                pass  # No bloquear si email falla
            
            messages.success(request, f'Reserva {"confirmada" if reserva.estado == "confirmada" else "enviada para aprobación"}.')
            return redirect('reservas:detalle', pk=reserva.pk)
    else:
        initial = {}
        if espacio_id:
            initial['espacio'] = espacio_id
        form = ReservaForm(initial=initial)
    
    return render(request, 'reservas/formulario.html', {
        'form': form,
        'titulo': 'Nueva reserva',
        'accion': 'Crear',
    })


@login_required
def editar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    
    # Solo el dueño, admin u operador
    if reserva.usuario != request.user and request.user.perfil.rol not in ['admin', 'operador']:
        messages.error(request, 'No tienes permisos para editar esta reserva.')
        return redirect('reservas:lista')
    
    # No se puede editar si ya está cancelada o completada
    if reserva.estado in ['cancelada', 'completada']:
        messages.error(request, 'No puedes editar una reserva cancelada o completada.')
        return redirect('reservas:detalle', pk=pk)
    
    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            
            HistorialReserva.objects.create(
                reserva=reserva,
                usuario=request.user,
                accion='modificada',
                comentario='Reserva modificada'
            )
            
            messages.success(request, 'Reserva actualizada.')
            return redirect('reservas:detalle', pk=pk)
    else:
        form = ReservaForm(instance=reserva)
    
    return render(request, 'reservas/formulario.html', {
        'form': form,
        'titulo': 'Editar reserva',
        'accion': 'Actualizar',
    })


@login_required
def cancelar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if not reserva.puede_cancelar(request.user):
        messages.error(request, 'No puedes cancelar esta reserva.')
        return redirect('reservas:detalle', pk=pk)
    
    if request.method == 'POST':
        reserva.estado = 'cancelada'
        reserva.save()
        
        HistorialReserva.objects.create(
            reserva=reserva,
            usuario=request.user,
            accion='cancelada',
            comentario=request.POST.get('comentario', '')
        )
        
        messages.success(request, 'Reserva cancelada.')
        return redirect('reservas:lista')
    
    return render(request, 'reservas/cancelar.html', {'reserva': reserva})


@login_required
@rol_requerido('admin', 'operador')
def confirmar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if reserva.estado != 'pendiente':
        messages.warning(request, 'Esta reserva no está pendiente.')
        return redirect('reservas:detalle', pk=pk)
    
    reserva.estado = 'confirmada'
    reserva.save()
    
    HistorialReserva.objects.create(
        reserva=reserva,
        usuario=request.user,
        accion='confirmada',
        comentario=f'Confirmada por {request.user.username}'
    )
    
    try:
        enviar_confirmacion_reserva(reserva)
    except:
        pass
    
    messages.success(request, 'Reserva confirmada.')
    return redirect('reservas:detalle', pk=pk)


@login_required
def calendario_reservas(request):
    """Vista calendario de reservas (semana actual)"""
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    
    reservas = Reserva.objects.filter(
        fecha__gte=inicio_semana,
        fecha__lte=fin_semana,
        estado='confirmada'
    ).select_related('espacio', 'usuario')
    
    dias = []
    for i in range(7):
        dia = inicio_semana + timedelta(days=i)
        reservas_dia = [r for r in reservas if r.fecha == dia]
        dias.append({
            'fecha': dia,
            'reservas': reservas_dia,
        })
    
    return render(request, 'reservas/calendario.html', {
        'dias': dias,
        'inicio_semana': inicio_semana,
        'fin_semana': fin_semana,
    })