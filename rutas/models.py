from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from config.choices import EstadoGeneral
from envios.querysets import RutaQuerySet


class Ruta(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    dias_entrega = models.PositiveIntegerField(default=1)
    estado = models.IntegerField(
        choices=EstadoGeneral.choices,
        default=EstadoGeneral.ACTIVO,
    )

    objects = RutaQuerySet.as_manager()

    class Meta:
        db_table = "rutas"
        verbose_name = "Ruta"
        verbose_name_plural = "Rutas"
        ordering = ["origen", "destino"]
        indexes = [
            models.Index(fields=["estado"], name="ruta_estado_idx"),
            models.Index(fields=["origen", "destino"], name="ruta_tramo_idx"),
        ]

    def clean(self):
        self.codigo = (self.codigo or "").strip().upper()
        self.origen = (self.origen or "").strip()
        self.destino = (self.destino or "").strip()
        self.descripcion = (self.descripcion or "").strip() or None

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo}: {self.origen} -> {self.destino}"
