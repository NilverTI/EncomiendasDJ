from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal


class GrupoArticulo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = "grupos_articulo"
        verbose_name = "Grupo de Artículo"
        verbose_name_plural = "Grupos de Artículos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class LineaArticulo(models.Model):
    grupo = models.ForeignKey(
        GrupoArticulo, on_delete=models.CASCADE,
        related_name="lineas",
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = "lineas_articulo"
        verbose_name = "Línea de Artículo"
        verbose_name_plural = "Líneas de Artículos"
        ordering = ["nombre"]
        unique_together = ["grupo", "nombre"]

    def __str__(self):
        return f"{self.grupo.nombre} - {self.nombre}"


class Articulo(models.Model):
    codigo_articulo = models.CharField(max_length=20, unique=True)
    codigo_barras = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.CharField(max_length=150)
    grupo = models.ForeignKey(
        GrupoArticulo, on_delete=models.PROTECT,
        related_name="articulos",
    )
    linea = models.ForeignKey(
        LineaArticulo, on_delete=models.PROTECT,
        related_name="articulos",
    )
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    precio_compra = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal("0.00"),
    )
    precio_venta = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal("0.00"),
    )
    estado = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "articulos"
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"
        ordering = ["codigo_articulo"]
        indexes = [
            models.Index(fields=["codigo_articulo"], name="art_codigo_idx"),
            models.Index(fields=["descripcion"], name="art_descripcion_idx"),
            models.Index(fields=["grupo", "linea"], name="art_grupo_linea_idx"),
        ]

    def clean(self):
        if len(self.codigo_articulo or "") < 4:
            raise ValidationError(
                {"codigo_articulo": "El código debe tener al menos 4 caracteres."}
            )
        if len(self.descripcion or "") < 5:
            raise ValidationError(
                {"descripcion": "La descripción debe tener al menos 5 caracteres."}
            )
        if self.linea_id and self.grupo_id:
            if self.linea.grupo_id != self.grupo_id:
                raise ValidationError(
                    {"linea": "La línea debe pertenecer al grupo seleccionado."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo_articulo} - {self.descripcion}"


class ListaPrecio(models.Model):
    articulo = models.ForeignKey(
        Articulo, on_delete=models.CASCADE,
        related_name="precios",
    )
    precio_1 = models.DecimalField(max_digits=10, decimal_places=2)
    precio_2 = models.DecimalField(
        max_digits=10, decimal_places=2,
        blank=True, null=True,
    )
    precio_3 = models.DecimalField(
        max_digits=10, decimal_places=2,
        blank=True, null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lista_precios"
        verbose_name = "Lista de Precio"
        verbose_name_plural = "Listas de Precios"

    def __str__(self):
        return f"{self.articulo.codigo_articulo} - P1: {self.precio_1}"


class OrdenCompraCliente(models.Model):
    ESTADO_CHOICES = [
        ("PE", "Pendiente"),
        ("CO", "Confirmada"),
        ("CA", "Cancelada"),
        ("EN", "Entregada"),
    ]
    numero_orden = models.CharField(max_length=20, unique=True)
    cliente_nombre = models.CharField(max_length=200)
    cliente_correo = models.EmailField(blank=True, null=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    estado = models.CharField(max_length=2, choices=ESTADO_CHOICES, default="PE")
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "ordenes_compra_cliente"
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Órdenes de Compra"
        ordering = ["-fecha_emision"]

    def __str__(self):
        return f"{self.numero_orden} - {self.cliente_nombre}"


class ItemOrdenCompraCliente(models.Model):
    orden = models.ForeignKey(
        OrdenCompraCliente, on_delete=models.CASCADE,
        related_name="items",
    )
    articulo = models.ForeignKey(
        Articulo, on_delete=models.PROTECT,
        related_name="items_orden",
    )
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "items_orden_compra_cliente"
        verbose_name = "Item de Orden"
        verbose_name_plural = "Items de Orden"

    def __str__(self):
        return f"{self.orden.numero_orden} - {self.articulo.codigo_articulo} x{self.cantidad}"
