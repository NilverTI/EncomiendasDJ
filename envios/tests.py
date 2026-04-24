from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from clientes.models import Cliente
from config.choices import EstadoEnvio, EstadoGeneral, TipoDocumento
from rutas.models import Ruta
from .models import Empleado, Encomienda


class EncomiendaTests(TestCase):
    def setUp(self):
        self.remitente = Cliente.objects.create(
            tipo_doc=TipoDocumento.DNI,
            nro_doc="12345678",
            nombres="Carlos",
            apellidos="Ramirez Torres",
            estado=EstadoGeneral.ACTIVO,
        )
        self.destinatario = Cliente.objects.create(
            tipo_doc=TipoDocumento.DNI,
            nro_doc="87654321",
            nombres="Ana",
            apellidos="Flores Diaz",
            estado=EstadoGeneral.ACTIVO,
        )
        self.ruta = Ruta.objects.create(
            codigo="LIM-TRU",
            origen="Lima",
            destino="Trujillo",
            precio_base=Decimal("25.00"),
            dias_entrega=2,
            estado=EstadoGeneral.ACTIVO,
        )
        self.empleado = Empleado.objects.create(
            codigo="EMP001",
            nombres="Luis",
            apellidos="Mendoza Cruz",
            cargo="Operador",
            email="luis@example.com",
            estado=EstadoGeneral.ACTIVO,
            fecha_ingreso=timezone.localdate(),
        )

    def test_validaciones_de_negocio(self):
        encomienda = Encomienda(
            codigo="ENC-2026-001",
            descripcion="Caja de prueba",
            peso_kg=Decimal("-1.00"),
            remitente=self.remitente,
            destinatario=self.remitente,
            ruta=self.ruta,
            empleado_registro=self.empleado,
            costo_envio=Decimal("25.00"),
            fecha_entrega_est=timezone.localdate() - timedelta(days=1),
        )

        with self.assertRaises(ValidationError) as ctx:
            encomienda.save()

        self.assertIn("peso_kg", ctx.exception.message_dict)
        self.assertIn("destinatario", ctx.exception.message_dict)
        self.assertIn("fecha_entrega_est", ctx.exception.message_dict)

    def test_crear_con_costo_calculado(self):
        encomienda = Encomienda.crear_con_costo_calculado(
            remitente=self.remitente,
            destinatario=self.destinatario,
            ruta=self.ruta,
            empleado=self.empleado,
            descripcion="Zapatos y ropa",
            peso_kg=Decimal("7.00"),
        )

        self.assertTrue(encomienda.codigo.startswith("ENC-"))
        self.assertEqual(encomienda.costo_envio, Decimal("30.00"))

    def test_cambiar_estado_crea_historial(self):
        encomienda = Encomienda.crear_con_costo_calculado(
            remitente=self.remitente,
            destinatario=self.destinatario,
            ruta=self.ruta,
            empleado=self.empleado,
            descripcion="Documentos",
            peso_kg=Decimal("1.50"),
        )

        encomienda.cambiar_estado(
            EstadoEnvio.EN_TRANSITO,
            empleado=self.empleado,
            observacion="Salida desde Lima",
        )

        self.assertEqual(encomienda.estado, EstadoEnvio.EN_TRANSITO)
        self.assertEqual(encomienda.historial.count(), 1)

    def test_querysets_personalizados(self):
        pendiente = Encomienda.crear_con_costo_calculado(
            remitente=self.remitente,
            destinatario=self.destinatario,
            ruta=self.ruta,
            empleado=self.empleado,
            descripcion="Pendiente",
            peso_kg=Decimal("1.00"),
        )
        retrasada = Encomienda.crear_con_costo_calculado(
            remitente=self.remitente,
            destinatario=self.destinatario,
            ruta=self.ruta,
            empleado=self.empleado,
            descripcion="Retrasada",
            peso_kg=Decimal("1.00"),
        )
        Encomienda.objects.filter(pk=retrasada.pk).update(
            fecha_entrega_est=timezone.localdate() - timedelta(days=1)
        )

        self.assertEqual(Encomienda.objects.pendientes().count(), 2)
        self.assertEqual(Encomienda.objects.activas().por_ruta(self.ruta).count(), 2)
        self.assertEqual(Encomienda.objects.con_retraso().count(), 1)
        self.assertEqual(Encomienda.objects.por_remitente(self.remitente).count(), 2)
        self.assertIn(pendiente, Encomienda.objects.con_relaciones())
