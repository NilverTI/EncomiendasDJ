from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "nro_doc",
        "tipo_doc",
        "apellidos",
        "nombres",
        "telefono",
        "estado",
        "fecha_registro",
    )
    list_filter = ("tipo_doc", "estado", "fecha_registro")
    search_fields = ("nro_doc", "apellidos", "nombres", "email")
    readonly_fields = ("fecha_registro",)
    ordering = ("apellidos", "nombres")
