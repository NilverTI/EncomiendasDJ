from django.db import models


class Ruta(models.Model):
    """Modelo para almacenar rutas de entrega"""
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('inactiva', 'Inactiva'),
        ('suspendida', 'Suspendida'),
    ]
    
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    distancia_km = models.FloatField()
    tiempo_estimado_horas = models.IntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activa')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ruta"
        verbose_name_plural = "Rutas"
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
