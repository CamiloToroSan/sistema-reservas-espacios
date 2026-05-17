from django.contrib import admin
from .models import Reserva, HistorialReserva


class HistorialInline(admin.TabularInline):
    model = HistorialReserva
    extra = 0
    readonly_fields = ('fecha',)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'espacio', 'usuario', 'fecha', 'hora_inicio', 'hora_fin', 'estado')
    list_filter = ('estado', 'fecha', 'espacio__tipo')
    search_fields = ('motivo', 'usuario__username', 'espacio__nombre')
    date_hierarchy = 'fecha'
    inlines = [HistorialInline]


@admin.register(HistorialReserva)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ('reserva', 'accion', 'usuario', 'fecha')
    list_filter = ('accion',)