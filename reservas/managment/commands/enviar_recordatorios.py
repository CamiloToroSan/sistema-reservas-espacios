from django.core.management.base import BaseCommand
from datetime import date, timedelta
from reservas.models import Reserva
from reservas.utils import enviar_recordatorio_reserva


class Command(BaseCommand):
    help = 'Envía recordatorios de reservas para el día siguiente'
    
    def handle(self, *args, **options):
        manana = date.today() + timedelta(days=1)
        reservas = Reserva.objects.filter(
            fecha=manana,
            estado='confirmada'
        ).select_related('usuario', 'espacio')
        
        enviados = 0
        for reserva in reservas:
            try:
                enviar_recordatorio_reserva(reserva)
                enviados += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ {reserva.usuario.email}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal: {enviados}/{reservas.count()} recordatorios enviados.'))