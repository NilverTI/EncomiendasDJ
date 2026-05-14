from django.contrib import admin
from django.utils.html import format_html

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
        "remitente_nombre",
        "destinatario_nombre",
        "ruta",
        "estado_badge",
        "peso_kg",
        "fecha_registro",
    )
    list_filter = ("estado", "ruta", "fecha_registro")
    search_fields = (
        "codigo",
        "remitente__apellidos",
        "destinatario__apellidos",
        "remitente__nro_doc",
    )
    readonly_fields = ("codigo", "fecha_registro", "fecha_entrega_real")
    autocomplete_fields = ("remitente", "destinatario", "ruta", "empleado_registro")
    list_select_related = ("remitente", "destinatario", "ruta", "empleado_registro")
    date_hierarchy = "fecha_registro"
    ordering = ("-fecha_registro",)
    list_per_page = 20
    inlines = (HistorialEstadoInline,)

    fieldsets = (
        ("Identificación", {
            "fields": ("codigo", "descripcion", "peso_kg", "volumen_cm3"),
        }),
        ("Partes", {
            "fields": ("remitente", "destinatario", "ruta", "empleado_registro"),
        }),
        ("Estado y fechas", {
            "fields": ("estado", "costo_envio", "fecha_registro", "fecha_entrega_est", "fecha_entrega_real"),
        }),
        ("Notas", {
            "classes": ("collapse",),
            "fields": ("observaciones",),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).con_relaciones()

    def remitente_nombre(self, obj):
        return obj.remitente.nombre_completo
    remitente_nombre.short_description = "Remitente"

    def destinatario_nombre(self, obj):
        return obj.destinatario.nombre_completo
    destinatario_nombre.short_description = "Destinatario"

    def estado_badge(self, obj):
        colores = {
            "PE": "#6c757d",
            "TR": "#0d6efd",
            "DE": "#fd7e14",
            "EN": "#198754",
            "DV": "#dc3545",
        }
        color = colores.get(obj.estado, "#6c757d")
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px">{}</span>',
            color,
            obj.get_estado_display(),
        )
    estado_badge.short_description = "Estado"


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
