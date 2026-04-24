from decimal import Decimal

from django.test import TestCase

from config.choices import EstadoGeneral
from .models import Ruta


class RutaQuerySetTests(TestCase):
    def setUp(self):
        Ruta.objects.create(
            codigo="LIM-TRU",
            origen="Lima",
            destino="Trujillo",
            precio_base=Decimal("25.00"),
            dias_entrega=2,
            estado=EstadoGeneral.ACTIVO,
        )
        Ruta.objects.create(
            codigo="CUS-ARE",
            origen="Cusco",
            destino="Arequipa",
            precio_base=Decimal("30.00"),
            dias_entrega=3,
            estado=EstadoGeneral.DE_BAJA,
        )

    def test_querysets_personalizados(self):
        self.assertEqual(Ruta.objects.activas().count(), 1)
        self.assertEqual(Ruta.objects.por_origen("Lima").count(), 1)
        self.assertEqual(Ruta.objects.por_destino("Arequipa").count(), 1)
