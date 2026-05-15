from django.db import models
from django.utils import timezone

from config.choices import EstadoEnvio, EstadoGeneral, TipoDocumento


class EncomiendaQuerySet(models.QuerySet):
    def pendientes(self):
        return self.filter(estado=EstadoEnvio.PENDIENTE)

    def en_transito(self):
        return self.filter(estado=EstadoEnvio.EN_TRANSITO)

    def entregadas(self):
        return self.filter(estado=EstadoEnvio.ENTREGADO)

    def devueltas(self):
        return self.filter(estado=EstadoEnvio.DEVUELTO)

    def activas(self):
        return self.filter(
            estado__in=[
                EstadoEnvio.PENDIENTE,
                EstadoEnvio.EN_TRANSITO,
                EstadoEnvio.EN_DESTINO,
            ]
        )

    def por_ruta(self, ruta):
        ruta_id = getattr(ruta, "pk", ruta)
        return self.filter(ruta_id=ruta_id)

    def por_remitente(self, cliente):
        cliente_id = getattr(cliente, "pk", cliente)
        return self.filter(remitente_id=cliente_id)

    def por_destinatario(self, cliente):
        cliente_id = getattr(cliente, "pk", cliente)
        return self.filter(destinatario_id=cliente_id)

    def en_transito_por_ruta(self, ruta):
        return self.en_transito().por_ruta(ruta)

    def con_retraso(self):
        return self.activas().filter(fecha_entrega_est__lt=timezone.localdate())

    def con_relaciones(self):
        return self.select_related(
            "remitente",
            "destinatario",
            "ruta",
            "empleado_registro",
        ).prefetch_related("historial__empleado")


class ClienteQuerySet(models.QuerySet):
    def activos(self):
        return self.filter(estado=EstadoGeneral.ACTIVO)

    def de_baja(self):
        return self.filter(estado=EstadoGeneral.DE_BAJA)

    def con_dni(self):
        return self.filter(tipo_doc=TipoDocumento.DNI)

    def buscar(self, termino):
        termino = (termino or "").strip()
        if not termino:
            return self
        return self.filter(
            models.Q(nombres__icontains=termino)
            | models.Q(apellidos__icontains=termino)
            | models.Q(nro_doc__icontains=termino)
        )


class RutaQuerySet(models.QuerySet):
    def activas(self):
        return self.filter(estado=EstadoGeneral.ACTIVO)

    def por_origen(self, ciudad):
        return self.filter(origen__icontains=ciudad)

    def por_destino(self, ciudad):
        return self.filter(destino__icontains=ciudad)
