from decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers
from django.utils import timezone

from clientes.models import Cliente
from rutas.models import Ruta
from envios.models import Encomienda, HistorialEstado, Empleado
from core.models import GrupoArticulo, LineaArticulo, Articulo, ListaPrecio, OrdenCompraCliente, ItemOrdenCompraCliente


class ClienteSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.ReadOnlyField()
    esta_activo = serializers.ReadOnlyField()

    class Meta:
        model = Cliente
        fields = [
            "id", "tipo_doc", "nro_doc",
            "nombres", "apellidos", "nombre_completo",
            "telefono", "email", "esta_activo",
        ]


class RutaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ruta
        fields = [
            "id", "codigo", "origen", "destino",
            "precio_base", "dias_entrega", "estado",
        ]


class HistorialEstadoSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.ReadOnlyField(source="empleado.__str__")
    estado_anterior_display = serializers.CharField(
        source="get_estado_anterior_display", read_only=True
    )
    estado_nuevo_display = serializers.CharField(
        source="get_estado_nuevo_display", read_only=True
    )

    class Meta:
        model = HistorialEstado
        fields = [
            "id", "estado_anterior", "estado_anterior_display",
            "estado_nuevo", "estado_nuevo_display",
            "empleado_nombre", "observacion", "fecha_cambio",
        ]


class EncomiendaBulkSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        encomiendas = [Encomienda(**item) for item in validated_data]
        return Encomienda.objects.bulk_create(encomiendas)

    def update(self, instances, validated_data):
        instance_map = {enc.id: enc for enc in instances}
        updated = []
        for item in validated_data:
            enc_id = item.pop("id", None)
            enc = instance_map.get(enc_id)
            if enc:
                for campo, valor in item.items():
                    setattr(enc, campo, valor)
                updated.append(enc)
        if updated:
            Encomienda.objects.bulk_update(
                updated,
                ["estado", "observaciones", "costo_envio"],
            )
        return updated


class EncomiendaSerializer(serializers.ModelSerializer):
    esta_entregada = serializers.ReadOnlyField()
    tiene_retraso = serializers.ReadOnlyField()
    dias_en_transito = serializers.ReadOnlyField()
    descripcion_corta = serializers.ReadOnlyField()
    estado_display = serializers.SerializerMethodField()

    class Meta:
        model = Encomienda
        fields = [
            "id", "codigo", "descripcion", "descripcion_corta",
            "peso_kg", "volumen_cm3", "costo_envio",
            "remitente", "destinatario", "ruta", "empleado_registro",
            "estado", "estado_display",
            "fecha_registro", "fecha_entrega_est", "fecha_entrega_real",
            "esta_entregada", "tiene_retraso", "dias_en_transito",
            "observaciones",
        ]
        read_only_fields = ["fecha_registro", "fecha_entrega_real", "empleado_registro"]
        list_serializer_class = EncomiendaBulkSerializer

    def get_estado_display(self, obj) -> str:
        return obj.get_estado_display()

    def validate_peso_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError("El peso debe ser mayor a 0 kg.")
        if value > 500:
            raise serializers.ValidationError("El peso maximo permitido es 500 kg.")
        return value

    def validate_codigo(self, value):
        if not value.startswith("ENC-"):
            raise serializers.ValidationError("El codigo debe comenzar con ENC-")
        return value.upper()

    def validate_costo_envio(self, value):
        if value < 0:
            raise serializers.ValidationError("El costo no puede ser negativo.")
        return value

    def validate(self, data):
        errors = {}
        if data.get("remitente") == data.get("destinatario"):
            errors["destinatario"] = (
                "El destinatario no puede ser el mismo que el remitente."
            )
        fecha_est = data.get("fecha_entrega_est")
        if fecha_est and fecha_est < timezone.now().date():
            errors["fecha_entrega_est"] = (
                "La fecha estimada no puede ser en el pasado."
            )
        ruta = data.get("ruta")
        costo = data.get("costo_envio")
        if ruta and costo and costo < float(ruta.precio_base):
            errors["costo_envio"] = (
                f"El costo minimo para esta ruta es S/ {ruta.precio_base}."
            )
        if errors:
            raise serializers.ValidationError(errors)
        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.ruta_id:
            data["ruta_codigo"] = instance.ruta.codigo
            data["ruta_destino"] = instance.ruta.destino
            data["ruta_origen"] = instance.ruta.origen
        data["costo_display"] = f"S/ {instance.costo_envio:.2f}"
        request = self.context.get("request")
        if request and not request.user.is_staff:
            data.pop("observaciones", None)
            data.pop("empleado_registro", None)
        colores = {
            "PE": "gray",
            "TR": "blue",
            "DE": "orange",
            "EN": "green",
            "DV": "red",
        }
        data["estado_color"] = colores.get(instance.estado, "gray")
        return data

    def to_internal_value(self, data):
        if hasattr(data, "_mutable"):
            data._mutable = True
        data = data.copy() if hasattr(data, "copy") else dict(data)
        if "codigo" in data and data["codigo"]:
            data["codigo"] = str(data["codigo"]).upper().strip()
        if "descripcion" in data and data["descripcion"]:
            data["descripcion"] = str(data["descripcion"]).strip()
        if "costo_envio" in data and data["costo_envio"]:
            try:
                costo = Decimal(str(data["costo_envio"]))
                data["costo_envio"] = str(
                    costo.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                )
            except Exception:
                pass
        return super().to_internal_value(data)


class EncomiendaListSerializer(serializers.ModelSerializer):
    remitente_nombre = serializers.ReadOnlyField(source="remitente.nombre_completo")
    destinatario_nombre = serializers.ReadOnlyField(source="destinatario.nombre_completo")
    ruta_destino = serializers.ReadOnlyField(source="ruta.destino")
    estado_display = serializers.SerializerMethodField()
    tiene_retraso = serializers.ReadOnlyField()

    class Meta:
        model = Encomienda
        fields = [
            "id", "codigo", "estado", "estado_display",
            "remitente_nombre", "destinatario_nombre",
            "ruta_destino", "peso_kg", "costo_envio",
            "fecha_registro", "fecha_entrega_est", "tiene_retraso",
        ]

    def get_estado_display(self, obj) -> str:
        return obj.get_estado_display()


class EncomiendaDetailSerializer(EncomiendaSerializer):
    remitente = ClienteSerializer(read_only=True)
    destinatario = ClienteSerializer(read_only=True)
    ruta = RutaSerializer(read_only=True)
    remitente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.activos(),
        write_only=True,
        source="remitente",
    )
    destinatario_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.activos(),
        write_only=True,
        source="destinatario",
    )
    ruta_id = serializers.PrimaryKeyRelatedField(
        queryset=Ruta.objects.activas(),
        write_only=True,
        source="ruta",
    )
    historial = serializers.SerializerMethodField()

    class Meta:
        model = Encomienda
        fields = [
            "id", "codigo", "descripcion", "peso_kg",
            "remitente", "remitente_id",
            "destinatario", "destinatario_id",
            "ruta", "ruta_id",
            "estado", "costo_envio",
            "fecha_registro", "fecha_entrega_est", "fecha_entrega_real",
            "esta_entregada", "tiene_retraso", "dias_en_transito",
            "historial", "observaciones",
        ]

    def get_historial(self, obj) -> list:
        return HistorialEstadoSerializer(
            obj.historial.all()[:5], many=True
        ).data


class EncomiendaV2Serializer(serializers.ModelSerializer):
    remitente = ClienteSerializer(read_only=True)
    destinatario = ClienteSerializer(read_only=True)
    ruta = RutaSerializer(read_only=True)
    remitente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.activos(),
        write_only=True,
        source="remitente",
    )
    destinatario_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.activos(),
        write_only=True,
        source="destinatario",
    )
    ruta_id = serializers.PrimaryKeyRelatedField(
        queryset=Ruta.objects.activas(),
        write_only=True,
        source="ruta",
    )
    dias_en_transito = serializers.ReadOnlyField()
    tiene_retraso = serializers.ReadOnlyField()
    esta_entregada = serializers.ReadOnlyField()
    descripcion_corta = serializers.ReadOnlyField()
    meta = serializers.SerializerMethodField()

    class Meta:
        model = Encomienda
        fields = [
            "id", "codigo", "descripcion", "descripcion_corta",
            "peso_kg", "volumen_cm3", "costo_envio",
            "remitente", "remitente_id",
            "destinatario", "destinatario_id",
            "ruta", "ruta_id",
            "estado", "fecha_registro", "fecha_entrega_est",
            "dias_en_transito", "tiene_retraso", "esta_entregada",
            "observaciones", "meta",
        ]
        read_only_fields = ["codigo", "fecha_registro"]

    def get_meta(self, obj) -> dict:
        return {
            "version": "v2",
            "generado": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "puede_editar": not obj.esta_entregada,
        }


# ── POS Serializers ─────────────────────────────────────────────────

class GrupoArticuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupoArticulo
        fields = ["id", "nombre", "descripcion", "estado"]


class LineaArticuloSerializer(serializers.ModelSerializer):
    grupo_nombre = serializers.ReadOnlyField(source="grupo.nombre")

    class Meta:
        model = LineaArticulo
        fields = ["id", "grupo", "grupo_nombre", "nombre", "descripcion", "estado"]


class ListaPrecioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListaPrecio
        fields = ["id", "articulo", "precio_1", "precio_2", "precio_3",
                   "created_at", "updated_at"]
        read_only_fields = ["articulo", "created_at", "updated_at"]


class ArticuloSerializer(serializers.ModelSerializer):
    grupo_nombre = serializers.ReadOnlyField(source="grupo.nombre")
    linea_nombre = serializers.ReadOnlyField(source="linea.nombre")
    precios = ListaPrecioSerializer(many=True, read_only=True)

    class Meta:
        model = Articulo
        fields = [
            "id", "codigo_articulo", "codigo_barras", "descripcion",
            "grupo", "grupo_nombre", "linea", "linea_nombre",
            "stock", "precio_compra", "precio_venta",
            "precios", "estado", "created_at", "updated_at",
        ]


class ArticuloListSerializer(serializers.ModelSerializer):
    grupo_nombre = serializers.ReadOnlyField(source="grupo.nombre")
    linea_nombre = serializers.ReadOnlyField(source="linea.nombre")

    class Meta:
        model = Articulo
        fields = [
            "id", "codigo_articulo", "descripcion",
            "grupo_nombre", "linea_nombre",
            "stock", "precio_venta", "estado",
        ]


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)
        if fields:
            allowed = set(fields)
            for field_name in set(self.fields):
                if field_name not in allowed:
                    self.fields.pop(field_name)


class ArticuloDynamicSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Articulo
        fields = "__all__"


class ItemOrdenSerializer(serializers.ModelSerializer):
    articulo_codigo = serializers.ReadOnlyField(source="articulo.codigo_articulo")
    articulo_descripcion = serializers.ReadOnlyField(source="articulo.descripcion")

    class Meta:
        model = ItemOrdenCompraCliente
        fields = [
            "id", "articulo", "articulo_codigo", "articulo_descripcion",
            "cantidad", "precio_unitario", "subtotal",
        ]


class OrdenSerializer(serializers.ModelSerializer):
    items = ItemOrdenSerializer(many=True, read_only=True)

    class Meta:
        model = OrdenCompraCliente
        fields = [
            "id", "numero_orden", "cliente_nombre", "cliente_correo",
            "fecha_emision", "total", "estado", "observaciones", "items",
        ]


class ArticuloCreateSerializer(serializers.ModelSerializer):
    precio_1 = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = Articulo
        fields = [
            "codigo_articulo", "codigo_barras", "descripcion",
            "grupo", "linea", "stock", "precio_compra", "precio_venta",
            "precio_1", "estado",
        ]

    def validate_codigo_articulo(self, value):
        if Articulo.objects.filter(codigo_articulo=value).exists():
            raise serializers.ValidationError("El código de artículo ya existe.")
        if len(value) < 4:
            raise serializers.ValidationError(
                "El código debe tener al menos 4 caracteres."
            )
        return value

    def validate_descripcion(self, value):
        if len(value) < 5:
            raise serializers.ValidationError(
                "La descripción debe tener al menos 5 caracteres."
            )
        if len(value) > 150:
            raise serializers.ValidationError(
                "La descripción no debe superar los 150 caracteres."
            )
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value

    def validate_linea(self, value):
        grupo_id = self.initial_data.get("grupo")
        if grupo_id and value.grupo_id != int(grupo_id):
            raise serializers.ValidationError(
                "La línea debe pertenecer al grupo seleccionado."
            )
        return value

    def create(self, validated_data):
        precio_1 = validated_data.pop("precio_1", None)
        articulo = Articulo.objects.create(**validated_data)
        if precio_1 is not None:
            ListaPrecio.objects.create(articulo=articulo, precio_1=precio_1)
        else:
            ListaPrecio.objects.create(articulo=articulo, precio_1=articulo.precio_venta)
        return articulo
