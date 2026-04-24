from django.contrib import admin

from .models import Empleado, Encomienda, HistorialEstado


class HistorialEstadoInline(admin.TabularInline):
    model = HistorialEstado
    extra = 0
    readonly_fields = ("estado_anterior", "estado_nuevo", "empleado", "fecha_cambio")
    can_delete = False


@admin.register(Encomienda)
class EncomiendaAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "remitente",
        "destinatario",
        "ruta",
        "empleado_registro",
        "estado",
        "fecha_entrega_est",
        "costo_envio",
    )
    list_filter = ("estado", "ruta", "empleado_registro", "fecha_registro")
    search_fields = (
        "codigo",
        "remitente__nro_doc",
        "remitente__apellidos",
        "destinatario__nro_doc",
        "destinatario__apellidos",
    )
    readonly_fields = ("fecha_registro", "costo_envio")
    autocomplete_fields = ("remitente", "destinatario", "ruta", "empleado_registro")
    list_select_related = ("remitente", "destinatario", "ruta", "empleado_registro")
    date_hierarchy = "fecha_registro"
    inlines = (HistorialEstadoInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).con_relaciones()


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "apellidos",
        "nombres",
        "cargo",
        "estado",
        "fecha_ingreso",
    )
    list_filter = ("estado", "cargo", "fecha_ingreso")
    search_fields = ("codigo", "apellidos", "nombres", "email")
    ordering = ("apellidos", "nombres")


@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display = (
        "encomienda",
        "estado_anterior",
        "estado_nuevo",
        "empleado",
        "fecha_cambio",
    )
    list_filter = ("estado_anterior", "estado_nuevo", "fecha_cambio")
    search_fields = ("encomienda__codigo", "empleado__codigo", "empleado__apellidos")
    readonly_fields = ("fecha_cambio",)
    list_select_related = ("encomienda", "empleado")
