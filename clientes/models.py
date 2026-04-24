from django.db import models

from config.choices import EstadoGeneral, TipoDocumento
from envios.querysets import ClienteQuerySet
from envios.validators import validar_nro_doc_dni


class Cliente(models.Model):
    tipo_doc = models.CharField(
        max_length=3,
        choices=TipoDocumento.choices,
        default=TipoDocumento.DNI,
    )
    nro_doc = models.CharField(max_length=15, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    estado = models.IntegerField(
        choices=EstadoGeneral.choices,
        default=EstadoGeneral.ACTIVO,
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = ClienteQuerySet.as_manager()

    class Meta:
        db_table = "clientes"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["apellidos", "nombres"]
        indexes = [
            models.Index(fields=["estado"], name="cliente_estado_idx"),
            models.Index(fields=["apellidos", "nombres"], name="cliente_nombre_idx"),
        ]

    def clean(self):
        self.nro_doc = (self.nro_doc or "").strip()
        self.nombres = (self.nombres or "").strip()
        self.apellidos = (self.apellidos or "").strip()
        self.email = (self.email or "").strip().lower() or None
        self.telefono = (self.telefono or "").strip() or None
        self.direccion = (self.direccion or "").strip() or None

        if self.tipo_doc == TipoDocumento.DNI:
            validar_nro_doc_dni(self.nro_doc)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def nombre_completo(self):
        return f"{self.apellidos}, {self.nombres}"

    @property
    def esta_activo(self):
        return self.estado == EstadoGeneral.ACTIVO

    @property
    def total_encomiendas_enviadas(self):
        return self.envios_como_remitente.count()

    def __str__(self):
        return f"{self.nro_doc} - {self.apellidos}, {self.nombres}"
