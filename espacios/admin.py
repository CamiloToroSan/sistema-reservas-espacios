from django.contrib import admin
from .models import Espacio, TipoEspacio

# Register your models here.

@admin.register(TipoEspacio)
class TipoEspacioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo', 'capacidad', 'ubicacion', 'estado')
    list_filter = ('tipo', 'estado')
    search_fields = ('codigo', 'nombre', 'ubicacion')
    list_editable = ('estado',)
