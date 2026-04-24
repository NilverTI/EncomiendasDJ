from django.core.exceptions import ValidationError
from django.test import TestCase

from config.choices import EstadoGeneral, TipoDocumento
from .models import Cliente


class ClienteModelTests(TestCase):
    def test_nombre_completo_y_estado(self):
        cliente = Cliente.objects.create(
            tipo_doc=TipoDocumento.DNI,
            nro_doc="12345678",
            nombres="Carlos",
            apellidos="Ramirez Torres",
            estado=EstadoGeneral.ACTIVO,
        )

        self.assertEqual(cliente.nombre_completo, "Ramirez Torres, Carlos")
        self.assertTrue(cliente.esta_activo)

    def test_valida_dni(self):
        cliente = Cliente(
            tipo_doc=TipoDocumento.DNI,
            nro_doc="1234",
            nombres="Carlos",
            apellidos="Ramirez",
        )

        with self.assertRaises(ValidationError):
            cliente.full_clean()

    def test_queryset_buscar_y_activos(self):
        Cliente.objects.create(
            tipo_doc=TipoDocumento.DNI,
            nro_doc="12345678",
            nombres="Carlos",
            apellidos="Ramirez",
            estado=EstadoGeneral.ACTIVO,
        )
        Cliente.objects.create(
            tipo_doc=TipoDocumento.DNI,
            nro_doc="87654321",
            nombres="Ana",
            apellidos="Flores",
            estado=EstadoGeneral.DE_BAJA,
        )

        self.assertEqual(Cliente.objects.activos().count(), 1)
        self.assertEqual(Cliente.objects.buscar("Ramirez").count(), 1)
