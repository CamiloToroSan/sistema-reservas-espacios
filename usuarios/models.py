from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    ROLES = [
        ('admin', 'Administrador'),
        ('docente', 'Docente'),
        ('estudiante', 'Estudiante'),
        ('operador', 'Operador'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROLES, default='estudiante')
    telefono = models.CharField(max_length=15, blank=True)
    documento = models.CharField(max_length=20, blank=True)
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"
    
    def es_admin(self):
        return self.rol == 'admin'
    
    def puede_gestionar_espacios(self):
        return self.rol in ['admin', 'operador']
    
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

# lo comente porque no dejaba crear mas roles desde superusuario

# @receiver(post_save, sender=User)
# def crear_perfil_usuario(sender, instance, created, **kwargs):
#     if created:
#         Perfil.objects.get_or_create(user=instance)