from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from espacios.models import Espacio


class Reserva(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas')
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE, related_name='reservas')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    motivo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    asistentes = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.espacio.codigo} | {self.fecha} {self.hora_inicio}"
    
    def get_absolute_url(self):
        return reverse('reservas:detalle', kwargs={'pk': self.pk})
    
    def duracion_horas(self):
        from datetime import datetime, timedelta
        inicio = datetime.combine(self.fecha, self.hora_inicio)
        fin = datetime.combine(self.fecha, self.hora_fin)
        return (fin - inicio).total_seconds() / 3600
    
    def puede_cancelar(self, user):
        if not user.is_authenticated:
            return False
        if user == self.usuario:
            return self.estado in ['pendiente', 'confirmada']
        return user.perfil.rol in ['admin', 'operador']
    
    def conflictos_con_otras(self):
        return Reserva.objects.filter(
            espacio=self.espacio,
            fecha=self.fecha,
            estado__in=['pendiente', 'confirmada'],
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio,
        ).exclude(pk=self.pk)
    
    def clean(self):
        super().clean()
        from datetime import date
        
        if self.fecha and self.fecha < date.today():
            raise ValidationError({'fecha': 'No puedes reservar en fechas pasadas.'})
        
        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            raise ValidationError({'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio.'})
        
        if self.espacio_id and self.espacio.estado != 'disponible':
            raise ValidationError({'espacio': f'El espacio no está disponible ({self.espacio.get_estado_display()}).'})
        
        if self.espacio_id and self.asistentes and self.asistentes > self.espacio.capacidad:
            raise ValidationError({'asistentes': f'Excede la capacidad del espacio ({self.espacio.capacidad}).'})
        
        if self.conflictos_con_otras().exists():
            raise ValidationError('Ya existe una reserva en ese horario para este espacio.')
    
    class Meta:
        ordering = ['-fecha', '-hora_inicio']
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'


class HistorialReserva(models.Model):
    ACCIONES = [
        ('creada', 'Creada'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('modificada', 'Modificada'),
        ('completada', 'Completada'),
    ]
    
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=20, choices=ACCIONES)
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.reserva} - {self.get_accion_display()}"
    
    class Meta:
        ordering = ['-fecha']