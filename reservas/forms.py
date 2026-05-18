from django import forms
from datetime import date, datetime
from .models import Reserva
from espacios.models import Espacio


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['espacio', 'fecha', 'hora_inicio', 'hora_fin', 'motivo', 'descripcion', 'asistentes']
        widgets = {
            'espacio': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Clase de cálculo'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'asistentes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar espacios disponibles
        self.fields['espacio'].queryset = Espacio.objects.filter(estado='disponible')
        # Mínimo de fecha es hoy
        self.fields['fecha'].widget.attrs['min'] = date.today().isoformat()
    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        espacio = cleaned_data.get('espacio')
        asistentes = cleaned_data.get('asistentes')
        
        # Fecha pasada
        if fecha and fecha < date.today():
            self.add_error('fecha', 'No puedes reservar en fechas pasadas.')
        
        # Hora inicio >= hora fin
        if hora_inicio and hora_fin:
            if hora_inicio >= hora_fin:
                self.add_error('hora_fin', 'La hora de fin debe ser posterior a la hora de inicio.')
            
            # Si es hoy, hora inicio no puede ser pasada
            if fecha == date.today():
                ahora = datetime.now().time()
                if hora_inicio < ahora:
                    self.add_error('hora_inicio', 'La hora de inicio no puede ser pasada.')
        
        # Capacidad
        if espacio and asistentes and asistentes > espacio.capacidad:
            self.add_error('asistentes', f'Excede capacidad del espacio ({espacio.capacidad}).')
        
        # Conflictos
        if fecha and hora_inicio and hora_fin and espacio:
            conflictos = Reserva.objects.filter(
                espacio=espacio,
                fecha=fecha,
                estado__in=['pendiente', 'confirmada'],
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio,
            )
            if self.instance.pk:
                conflictos = conflictos.exclude(pk=self.instance.pk)
            
            if conflictos.exists():
                self.add_error(None, 'Ya existe una reserva en ese horario. Verifica disponibilidad.')
        
        return cleaned_data