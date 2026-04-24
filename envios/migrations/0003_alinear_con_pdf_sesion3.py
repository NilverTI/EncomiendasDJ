import datetime
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import migrations, models
import django.db.models.deletion

import config.choices
import envios.validators


def migrar_empleados(apps, schema_editor):
    Empleado = apps.get_model("envios", "Empleado")
    estado_map = {
        "activo": config.choices.EstadoGeneral.ACTIVO,
        "inactivo": config.choices.EstadoGeneral.DE_BAJA,
        "suspendida": config.choices.EstadoGeneral.DE_BAJA,
    }
    for empleado in Empleado.objects.order_by("id"):
        empleado.codigo_tmp = f"EMP{empleado.id:03d}"
        empleado.estado_tmp = estado_map.get(
            empleado.estado,
            config.choices.EstadoGeneral.ACTIVO,
        )
        if not empleado.fecha_ingreso:
            empleado.fecha_ingreso = datetime.date.today()
        empleado.save(
            update_fields=["codigo_tmp", "estado_tmp", "fecha_ingreso"]
        )


def migrar_estado_encomiendas(apps, schema_editor):
    Encomienda = apps.get_model("envios", "Encomienda")
    estado_map = {
        "pendiente": config.choices.EstadoEnvio.PENDIENTE,
        "en_transito": config.choices.EstadoEnvio.EN_TRANSITO,
        "entregada": config.choices.EstadoEnvio.ENTREGADO,
        "cancelada": config.choices.EstadoEnvio.DEVUELTO,
        "retenida": config.choices.EstadoEnvio.EN_DESTINO,
    }
    for encomienda in Encomienda.objects.all():
        encomienda.estado_tmp = estado_map.get(
            encomienda.estado,
            config.choices.EstadoEnvio.PENDIENTE,
        )
        encomienda.save(update_fields=["estado_tmp"])


def migrar_estado_historial(apps, schema_editor):
    HistorialEstado = apps.get_model("envios", "HistorialEstado")
    estado_map = {
        "pendiente": config.choices.EstadoEnvio.PENDIENTE,
        "en_transito": config.choices.EstadoEnvio.EN_TRANSITO,
        "entregada": config.choices.EstadoEnvio.ENTREGADO,
        "cancelada": config.choices.EstadoEnvio.DEVUELTO,
        "retenida": config.choices.EstadoEnvio.EN_DESTINO,
    }
    for historial in HistorialEstado.objects.all():
        historial.estado_anterior_tmp = estado_map.get(
            historial.estado_anterior,
            config.choices.EstadoEnvio.PENDIENTE,
        )
        historial.estado_nuevo_tmp = estado_map.get(
            historial.estado_nuevo,
            config.choices.EstadoEnvio.PENDIENTE,
        )
        historial.save(
            update_fields=["estado_anterior_tmp", "estado_nuevo_tmp"]
        )


class Migration(migrations.Migration):
    dependencies = [
        ("clientes", "0003_alinear_con_pdf_sesion3"),
        ("rutas", "0003_alinear_con_pdf_sesion3"),
        ("envios", "0002_sesion3_orm_entregable"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="empleado",
            options={
                "ordering": ["apellidos"],
                "verbose_name": "Empleado",
                "verbose_name_plural": "Empleados",
            },
        ),
        migrations.RenameField(
            model_name="empleado",
            old_name="nombre",
            new_name="nombres",
        ),
        migrations.RenameField(
            model_name="empleado",
            old_name="apellido",
            new_name="apellidos",
        ),
        migrations.AddField(
            model_name="empleado",
            name="codigo_tmp",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="empleado",
            name="estado_tmp",
            field=models.IntegerField(
                choices=config.choices.EstadoGeneral.choices,
                default=config.choices.EstadoGeneral.ACTIVO,
            ),
        ),
        migrations.AddField(
            model_name="empleado",
            name="fecha_ingreso",
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.RunPython(migrar_empleados, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="empleado",
            name="tipo_documento",
        ),
        migrations.RemoveField(
            model_name="empleado",
            name="numero_documento",
        ),
        migrations.RemoveField(
            model_name="empleado",
            name="estado",
        ),
        migrations.RemoveField(
            model_name="empleado",
            name="fecha_creacion",
        ),
        migrations.RenameField(
            model_name="empleado",
            old_name="codigo_tmp",
            new_name="codigo",
        ),
        migrations.RenameField(
            model_name="empleado",
            old_name="estado_tmp",
            new_name="estado",
        ),
        migrations.AlterField(
            model_name="empleado",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name="empleado",
            name="codigo",
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name="empleado",
            name="cargo",
            field=models.CharField(max_length=80),
        ),
        migrations.AlterField(
            model_name="empleado",
            name="telefono",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name="empleado",
            name="estado",
            field=models.IntegerField(
                choices=config.choices.EstadoGeneral.choices,
                default=config.choices.EstadoGeneral.ACTIVO,
            ),
        ),
        migrations.AlterField(
            model_name="empleado",
            name="fecha_ingreso",
            field=models.DateField(),
        ),
        migrations.AlterModelTable(
            name="empleado",
            table="empleados",
        ),
        migrations.AlterModelOptions(
            name="encomienda",
            options={
                "ordering": ["-fecha_registro"],
                "verbose_name": "Encomienda",
                "verbose_name_plural": "Encomiendas",
            },
        ),
        migrations.RenameField(
            model_name="encomienda",
            old_name="numero_seguimiento",
            new_name="codigo",
        ),
        migrations.RenameField(
            model_name="encomienda",
            old_name="empleado_responsable",
            new_name="empleado_registro",
        ),
        migrations.RenameField(
            model_name="encomienda",
            old_name="fecha_creacion",
            new_name="fecha_registro",
        ),
        migrations.RenameField(
            model_name="encomienda",
            old_name="fecha_estimada_entrega",
            new_name="fecha_entrega_est",
        ),
        migrations.AddField(
            model_name="encomienda",
            name="volumen_cm3",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=12,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="encomienda",
            name="estado_tmp",
            field=models.CharField(
                choices=config.choices.EstadoEnvio.choices,
                default=config.choices.EstadoEnvio.PENDIENTE,
                max_length=2,
            ),
        ),
        migrations.RunPython(
            migrar_estado_encomiendas,
            migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name="encomienda",
            name="estado",
        ),
        migrations.RemoveField(
            model_name="encomienda",
            name="fecha_actualizacion",
        ),
        migrations.RemoveField(
            model_name="encomienda",
            name="fecha_envio",
        ),
        migrations.RemoveField(
            model_name="encomienda",
            name="dimensiones",
        ),
        migrations.RemoveField(
            model_name="encomienda",
            name="valor_declarado",
        ),
        migrations.RemoveField(
            model_name="encomienda",
            name="direccion_entrega",
        ),
        migrations.RemoveField(
            model_name="encomienda",
            name="nombre_destinatario",
        ),
        migrations.RemoveField(
            model_name="encomienda",
            name="telefono_destinatario",
        ),
        migrations.RenameField(
            model_name="encomienda",
            old_name="estado_tmp",
            new_name="estado",
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="codigo",
            field=models.CharField(
                max_length=20,
                unique=True,
                validators=[envios.validators.validar_codigo_encomienda],
            ),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="peso_kg",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=8,
                validators=[
                    envios.validators.validar_peso_positivo,
                    MinValueValidator(
                        Decimal("0.01"),
                        message="El peso minimo es 0.01 kg",
                    ),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="remitente",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="envios_como_remitente",
                to="clientes.cliente",
            ),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="destinatario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="envios_como_destinatario",
                to="clientes.cliente",
            ),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="ruta",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="encomiendas",
                to="rutas.ruta",
            ),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="empleado_registro",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="encomiendas_registradas",
                to="envios.empleado",
            ),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="estado",
            field=models.CharField(
                choices=config.choices.EstadoEnvio.choices,
                default=config.choices.EstadoEnvio.PENDIENTE,
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="costo_envio",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                validators=[MinValueValidator(Decimal("0"))],
            ),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="fecha_entrega_est",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="fecha_entrega_real",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="observaciones",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterModelTable(
            name="encomienda",
            table="encomiendas",
        ),
        migrations.AlterModelOptions(
            name="historialestado",
            options={"ordering": ["-fecha_cambio"]},
        ),
        migrations.AddField(
            model_name="historialestado",
            name="estado_anterior_tmp",
            field=models.CharField(
                choices=config.choices.EstadoEnvio.choices,
                default=config.choices.EstadoEnvio.PENDIENTE,
                max_length=2,
            ),
        ),
        migrations.AddField(
            model_name="historialestado",
            name="estado_nuevo_tmp",
            field=models.CharField(
                choices=config.choices.EstadoEnvio.choices,
                default=config.choices.EstadoEnvio.PENDIENTE,
                max_length=2,
            ),
        ),
        migrations.RunPython(
            migrar_estado_historial,
            migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name="historialestado",
            name="estado_anterior",
        ),
        migrations.RemoveField(
            model_name="historialestado",
            name="estado_nuevo",
        ),
        migrations.RenameField(
            model_name="historialestado",
            old_name="estado_anterior_tmp",
            new_name="estado_anterior",
        ),
        migrations.RenameField(
            model_name="historialestado",
            old_name="estado_nuevo_tmp",
            new_name="estado_nuevo",
        ),
        migrations.AlterField(
            model_name="historialestado",
            name="encomienda",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="historial",
                to="envios.encomienda",
            ),
        ),
        migrations.AlterField(
            model_name="historialestado",
            name="estado_anterior",
            field=models.CharField(
                choices=config.choices.EstadoEnvio.choices,
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="historialestado",
            name="estado_nuevo",
            field=models.CharField(
                choices=config.choices.EstadoEnvio.choices,
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="historialestado",
            name="observacion",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="historialestado",
            name="empleado",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="cambios_estado",
                to="envios.empleado",
            ),
        ),
        migrations.AlterModelTable(
            name="historialestado",
            table="historial_estados",
        ),
    ]
