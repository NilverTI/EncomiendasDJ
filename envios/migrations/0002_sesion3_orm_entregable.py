# Generated manually for Sesion 3 ORM

import datetime
from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

import config.choices
import envios.validators


class Migration(migrations.Migration):
    dependencies = [
        ("clientes", "0002_sesion3_cliente_campos"),
        ("rutas", "0002_sesion3_ruta_campos"),
        ("envios", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="encomienda",
            options={
                "ordering": ["-fecha_envio", "-fecha_creacion"],
                "verbose_name": "Encomienda",
                "verbose_name_plural": "Encomiendas",
            },
        ),
        migrations.AlterModelTable(
            name="encomienda",
            table="envios_encomienda",
        ),
        migrations.CreateModel(
            name="Empleado",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=100)),
                ("apellido", models.CharField(max_length=100)),
                (
                    "tipo_documento",
                    models.CharField(
                        choices=config.choices.TipoDocumento.choices,
                        default=config.choices.TipoDocumento.DNI,
                        max_length=20,
                    ),
                ),
                ("numero_documento", models.CharField(max_length=20, unique=True)),
                ("cargo", models.CharField(max_length=100)),
                ("telefono", models.CharField(max_length=20)),
                ("email", models.EmailField(blank=True, max_length=254)),
                (
                    "estado",
                    models.CharField(
                        choices=config.choices.EstadoGeneral.choices,
                        default=config.choices.EstadoGeneral.ACTIVO,
                        max_length=20,
                    ),
                ),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "envios_empleado",
                "ordering": ["apellido", "nombre"],
                "verbose_name": "Empleado",
                "verbose_name_plural": "Empleados",
            },
        ),
        migrations.RenameField(
            model_name="encomienda",
            old_name="cliente",
            new_name="remitente",
        ),
        migrations.RenameField(
            model_name="encomienda",
            old_name="destinatario",
            new_name="nombre_destinatario",
        ),
        migrations.RenameField(
            model_name="encomienda",
            old_name="fecha_entrega",
            new_name="fecha_entrega_real",
        ),
        migrations.AddField(
            model_name="encomienda",
            name="costo_envio",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="encomienda",
            name="destinatario",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="encomiendas_recibidas",
                to="clientes.cliente",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="encomienda",
            name="empleado_responsable",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="encomiendas_asignadas",
                to="envios.empleado",
            ),
        ),
        migrations.AddField(
            model_name="encomienda",
            name="fecha_envio",
            field=models.DateField(default=django.utils.timezone.localdate),
        ),
        migrations.AddField(
            model_name="encomienda",
            name="fecha_estimada_entrega",
            field=models.DateField(default=django.utils.timezone.localdate),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="estado",
            field=models.CharField(
                choices=config.choices.EstadoEnvio.choices,
                default=config.choices.EstadoEnvio.PENDIENTE,
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="fecha_envio",
            field=models.DateField(default=django.utils.timezone.localdate),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="fecha_estimada_entrega",
            field=models.DateField(default=django.utils.timezone.localdate),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="fecha_entrega_real",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="nombre_destinatario",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="numero_seguimiento",
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
                validators=[envios.validators.validar_peso_positivo],
            ),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="remitente",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="encomiendas_enviadas",
                to="clientes.cliente",
            ),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="telefono_destinatario",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="valor_declarado",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.CreateModel(
            name="HistorialEstado",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "estado_anterior",
                    models.CharField(
                        blank=True,
                        choices=config.choices.EstadoEnvio.choices,
                        max_length=20,
                    ),
                ),
                (
                    "estado_nuevo",
                    models.CharField(
                        choices=config.choices.EstadoEnvio.choices,
                        max_length=20,
                    ),
                ),
                ("observacion", models.TextField(blank=True)),
                ("fecha_cambio", models.DateTimeField(auto_now_add=True)),
                (
                    "empleado",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="historiales_estado",
                        to="envios.empleado",
                    ),
                ),
                (
                    "encomienda",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="historial_estados",
                        to="envios.encomienda",
                    ),
                ),
            ],
            options={
                "db_table": "envios_historialestado",
                "ordering": ["-fecha_cambio"],
                "verbose_name": "Historial de estado",
                "verbose_name_plural": "Historiales de estado",
            },
        ),
    ]
