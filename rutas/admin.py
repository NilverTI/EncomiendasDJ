from django.contrib import admin
from .models import Ruta


@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'origen', 'destino', 'distancia_km', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion', 'origen')
    search_fields = ('codigo', 'nombre', 'origen', 'destino')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        ('Información de Ruta', {
            'fields': ('codigo', 'nombre', 'descripcion')
        }),
        ('Trayecto', {
            'fields': ('origen', 'destino', 'distancia_km', 'tiempo_estimado_horas')
        }),
        ('Estado', {
            'fields': ('estado', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )
