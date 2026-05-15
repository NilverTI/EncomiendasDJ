import uuid
from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import F, Q
from django.utils import timezone

from clientes.models import Cliente
from config.choices import EstadoEnvio, EstadoGeneral
from envios.querysets import EncomiendaQuerySet
from envios.validators import validar_codigo_encomienda, validar_peso_positivo
from rutas.models import Ruta


class Empleado(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cargo = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    estado = models.IntegerField(
        choices=EstadoGeneral.choices,
        default=EstadoGeneral.ACTIVO,
    )
    fecha_ingreso = models.DateField()

    class Meta:
        db_table = "empleados"
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ["apellidos", "nombres"]
        indexes = [
            models.Index(fields=["estado"], name="empleado_estado_idx"),
        ]

    def clean(self):
        self.codigo = (self.codigo or "").strip().upper()
        self.nombres = (self.nombres or "").strip()
        self.apellidos = (self.apellidos or "").strip()
        self.cargo = (self.cargo or "").strip()
        self.email = (self.email or "").strip().lower()
        self.telefono = (self.telefono or "").strip() or None

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.apellidos}, {self.nombres}"


class Encomienda(models.Model):
    codigo = models.CharField(
        max_length=20,
        unique=True,
        validators=[validar_codigo_encomienda],
    )
    descripcion = models.TextField()
    peso_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[
            validar_peso_positivo,
            MinValueValidator(Decimal("0.01"), message="El peso minimo es 0.01 kg"),
        ],
    )
    volumen_cm3 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    remitente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="envios_como_remitente",
    )
    destinatario = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="envios_como_destinatario",
    )
    ruta = models.ForeignKey(
        Ruta,
        on_delete=models.PROTECT,
        related_name="encomiendas",
    )
    empleado_registro = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="encomiendas_registradas",
    )
    estado = models.CharField(
        max_length=2,
        choices=EstadoEnvio.choices,
        default=EstadoEnvio.PENDIENTE,
    )
    costo_envio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, db_index=True)
    fecha_entrega_est = models.DateField(null=True, blank=True, db_index=True)
    fecha_entrega_real = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)

    objects = EncomiendaQuerySet.as_manager()

    class Meta:
        db_table = "encomiendas"
        verbose_name = "Encomienda"
        verbose_name_plural = "Encomiendas"
        ordering = ["-fecha_registro"]
        indexes = [
            models.Index(fields=["estado", "fecha_entrega_est"], name="encomienda_estado_fecha_idx"),
            models.Index(fields=["ruta", "estado"], name="encomienda_ruta_estado_idx"),
            models.Index(fields=["remitente", "estado"], name="encomienda_rem_estado_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~Q(remitente=F("destinatario")),
                name="encomienda_partes_distintas_chk",
            ),
        ]

    def clean(self):
        self.codigo = (self.codigo or "").strip().upper()
        self.descripcion = (self.descripcion or "").strip()
        self.observaciones = (self.observaciones or "").strip() or None

        errors = {}
        today = timezone.localdate()

        if self.remitente_id and self.destinatario_id and self.remitente_id == self.destinatario_id:
            errors["destinatario"] = ValidationError(
                "El destinatario no puede ser el mismo que el remitente."
            )

        if self.fecha_entrega_est:
            fecha_estimacion_modificada = self._state.adding
            if self.pk and not fecha_estimacion_modificada:
                fecha_actual = (
                    type(self)
                    .objects.filter(pk=self.pk)
                    .values_list("fecha_entrega_est", flat=True)
                    .first()
                )
                fecha_estimacion_modificada = fecha_actual != self.fecha_entrega_est

            if fecha_estimacion_modificada and self.fecha_entrega_est < today:
                errors["fecha_entrega_est"] = ValidationError(
                    "La fecha de entrega estimada no puede ser en el pasado."
                )

        if self.fecha_entrega_est and self.fecha_entrega_real:
            if self.fecha_entrega_real < self.fecha_entrega_est:
                errors["fecha_entrega_real"] = ValidationError(
                    "La fecha de entrega real no puede ser antes de la estimada."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.ruta_id and self.peso_kg is not None and not self.costo_envio:
            self.costo_envio = self.calcular_costo()

        if self.estado == EstadoEnvio.ENTREGADO and self.fecha_entrega_real is None:
            self.fecha_entrega_real = timezone.localdate()

        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def esta_entregada(self) -> bool:
        return self.estado == EstadoEnvio.ENTREGADO

    @property
    def esta_en_transito(self) -> bool:
        return self.estado == EstadoEnvio.EN_TRANSITO

    @property
    def dias_en_transito(self) -> int:
        if not self.fecha_registro:
            return 0
        return (timezone.now().date() - self.fecha_registro.date()).days

    @property
    def tiene_retraso(self) -> bool:
        if not self.fecha_entrega_est or self.esta_entregada:
            return False
        return timezone.localdate() > self.fecha_entrega_est

    @property
    def descripcion_corta(self) -> str:
        return (
            f"{self.descripcion[:50]}..."
            if len(self.descripcion) > 50
            else self.descripcion
        )

    def cambiar_estado(self, nuevo_estado, empleado, observacion=""):
        if nuevo_estado not in EstadoEnvio.values:
            raise ValueError("El nuevo estado no es valido.")

        if nuevo_estado == self.estado:
            raise ValueError(
                f"La encomienda ya se encuentra en estado {self.get_estado_display()}"
            )

        with transaction.atomic():
            estado_anterior = self.estado
            self.estado = nuevo_estado
            if nuevo_estado == EstadoEnvio.ENTREGADO:
                self.fecha_entrega_real = timezone.localdate()
            self.save()

            HistorialEstado.objects.create(
                encomienda=self,
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado,
                empleado=empleado,
                observacion=observacion,
            )

        return self

    def calcular_costo(self):
        precio_por_kg_extra = Decimal("2.50")
        peso_base = Decimal("5.00")
        costo = Decimal(self.ruta.precio_base)
        if self.peso_kg > peso_base:
            costo += (self.peso_kg - peso_base) * precio_por_kg_extra
        return costo.quantize(Decimal("0.01"))

    @classmethod
    def crear_con_costo_calculado(
        cls,
        remitente,
        destinatario,
        ruta,
        empleado,
        descripcion,
        peso_kg,
        **kwargs,
    ):
        kwargs.setdefault(
            "codigo",
            f"ENC-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}",
        )
        kwargs.setdefault(
            "fecha_entrega_est",
            timezone.localdate() + timedelta(days=ruta.dias_entrega),
        )

        encomienda = cls(
            descripcion=descripcion,
            peso_kg=peso_kg,
            remitente=remitente,
            destinatario=destinatario,
            ruta=ruta,
            empleado_registro=empleado,
            **kwargs,
        )
        encomienda.costo_envio = encomienda.calcular_costo()
        encomienda.save()
        return encomienda

    def __str__(self):
        return f"{self.codigo} [{self.get_estado_display()}]"


class HistorialEstado(models.Model):
    encomienda = models.ForeignKey(
        Encomienda,
        on_delete=models.CASCADE,
        related_name="historial",
    )
    estado_anterior = models.CharField(max_length=2, choices=EstadoEnvio.choices)
    estado_nuevo = models.CharField(max_length=2, choices=EstadoEnvio.choices)
    observacion = models.TextField(blank=True, null=True)
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="cambios_estado",
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "historial_estados"
        verbose_name = "Historial de estado"
        verbose_name_plural = "Historiales de estado"
        ordering = ["-fecha_cambio"]
        indexes = [
            models.Index(fields=["encomienda", "fecha_cambio"], name="historial_enc_fecha_idx"),
        ]

    def __str__(self):
        return f"{self.encomienda.codigo}: {self.estado_anterior}->{self.estado_nuevo}"
