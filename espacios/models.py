from django.db import models
from django.urls import reverse

# Create your models here.

class TipoEspacio(models.Model):
    nombre = models.CharField(max_lenght=50, unique=True)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_lenght=50, default='bi-building', help_text='Clase de Bootstrap Icons')

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Tipo de Espacio'
        verbose_name_plural = 'Tipos de Espacios'
        ordering = ['nombre']

class Espacio(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('mantenimiento', 'Mantenimiento'),
        ('inactivo', 'Inactivo'),
    ]

    codigo = models.CharField(max_lenght=20, unique=True, help_text='Ej: AULA-101, LAB-205')
    nombre = models.CharField(max_lenght=100)
    tipo = models.ForeignKey(TipoEspacio, on_delete=models.PROTECT, related_name='espacios')
    capacidad = models.PositiveIntegerField()
    descripcion = models.TextField(blank=True)
    equipamiento = models.TextField(blank=True, help_text='Recursos Disponibles')
    estado = models.CharField(max_lenght=20, choices=ESTADOS, default='disponible')
    foto = models.ImageField(upload_to='espacios/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'
    
    def get_absolute_url(self):
       return reverse('espacios:detalle', kwargs={'pk': self.pk})
    
    def total_reservas(self):
        return self.reservas.count()
    
    def reservas_activas(self):
        return self.reservas.filter(estado__in=['pendiente', 'confirmada']).count()
    
    class Meta:
        ordering = ['codigo']
