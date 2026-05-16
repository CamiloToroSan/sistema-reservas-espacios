from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Perfil


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'


class UserAdminPersonalizado(UserAdmin):
    inlines = (PerfilInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_rol', 'is_staff')
    
    def get_rol(self, obj):
        try:
            return obj.perfil.get_rol_display()
        except:
            return '-'
    get_rol.short_description = 'Rol'


admin.site.unregister(User)
admin.site.register(User, UserAdminPersonalizado)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol', 'documento', 'telefono', 'fecha_registro')
    list_filter = ('rol',)
    search_fields = ('user__username', 'user__email', 'documento')