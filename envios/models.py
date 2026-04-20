from django.db import models
from clientes.models import Cliente
from rutas.models import Ruta


class Encomienda(models.Model):
    """Modelo principal para encomiendas/envíos"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_transito', 'En Tránsito'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
        ('retenida', 'Retenida'),
    ]
    
    numero_seguimiento = models.CharField(max_length=50, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='encomiendas')
    ruta = models.ForeignKey(Ruta, on_delete=models.PROTECT, related_name='encomiendas')
    
    descripcion = models.TextField()
    peso_kg = models.FloatField()
    dimensiones = models.CharField(max_length=100, blank=True, null=True)
    valor_declarado = models.DecimalField(max_digits=10, decimal_places=2)
    
    direccion_entrega = models.TextField()
    destinatario = models.CharField(max_length=100)
    telefono_destinatario = models.CharField(max_length=20)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_entrega = models.DateTimeField(blank=True, null=True)
    
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Encomienda"
        verbose_name_plural = "Encomiendas"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.numero_seguimiento} - {self.cliente.nombre} ({self.estado})"
