from django.contrib import admin
from .models import Encomienda


@admin.register(Encomienda)
class EncomiendaAdmin(admin.ModelAdmin):
    list_display = ('numero_seguimiento', 'cliente', 'ruta', 'estado', 'fecha_creacion', 'destinatario')
    list_filter = ('estado', 'fecha_creacion', 'ruta')
    search_fields = ('numero_seguimiento', 'cliente__nombre', 'cliente__apellido', 'destinatario', 'telefono_destinatario')
    readonly_fields = ('numero_seguimiento', 'fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        ('Información de Envío', {
            'fields': ('numero_seguimiento', 'cliente', 'ruta', 'estado')
        }),
        ('Descripción del Paquete', {
            'fields': ('descripcion', 'peso_kg', 'dimensiones', 'valor_declarado')
        }),
        ('Datos de Entrega', {
            'fields': ('direccion_entrega', 'destinatario', 'telefono_destinatario')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion', 'fecha_entrega'),
            'classes': ('collapse',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
    )
