from django.core.mail import send_mail
from django.conf import settings


def enviar_confirmacion_reserva(reserva):
    asunto = f'Reserva confirmada - {reserva.espacio.codigo}'
    mensaje = f"""
Hola {reserva.usuario.get_full_name() or reserva.usuario.username},

Tu reserva ha sido {reserva.get_estado_display()}.

Detalles:
- Espacio: {reserva.espacio.nombre} ({reserva.espacio.codigo})
- Ubicación: {reserva.espacio.ubicacion}
- Fecha: {reserva.fecha}
- Horario: {reserva.hora_inicio} - {reserva.hora_fin}
- Motivo: {reserva.motivo}

Gracias por usar el sistema de reservas.
"""
    
    if reserva.usuario.email:
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [reserva.usuario.email],
            fail_silently=True,
        )


def enviar_recordatorio_reserva(reserva):
    asunto = f'Recordatorio: reserva mañana - {reserva.espacio.codigo}'
    mensaje = f"""
Hola {reserva.usuario.get_full_name() or reserva.usuario.username},

Te recordamos tu reserva para mañana:

- Espacio: {reserva.espacio.nombre}
- Fecha: {reserva.fecha}
- Horario: {reserva.hora_inicio} - {reserva.hora_fin}
- Motivo: {reserva.motivo}

¡Nos vemos pronto!
"""
    
    if reserva.usuario.email:
        send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [reserva.usuario.email], fail_silently=True)