from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'telefono', 'ciudad', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'ciudad', 'fecha_creacion')
    search_fields = ('nombre', 'apellido', 'email', 'telefono')
    readonly_fields = ('fecha_creacion',)
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'email', 'telefono')
        }),
        ('Dirección', {
            'fields': ('direccion', 'ciudad')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion')
        }),
    )
