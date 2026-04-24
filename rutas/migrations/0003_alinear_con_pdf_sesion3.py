import math

from django.db import migrations, models

import config.choices


def migrar_rutas(apps, schema_editor):
    Ruta = apps.get_model("rutas", "Ruta")
    estado_map = {
        "activo": config.choices.EstadoGeneral.ACTIVO,
        "inactivo": config.choices.EstadoGeneral.DE_BAJA,
        "suspendida": config.choices.EstadoGeneral.DE_BAJA,
    }
    for ruta in Ruta.objects.all():
        ruta.estado_tmp = estado_map.get(
            ruta.estado,
            config.choices.EstadoGeneral.ACTIVO,
        )
        ruta.dias_entrega = max(1, math.ceil((ruta.dias_entrega or 1) / 24))
        ruta.save(update_fields=["estado_tmp", "dias_entrega"])


class Migration(migrations.Migration):
    dependencies = [
        ("rutas", "0002_sesion3_ruta_campos"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="ruta",
            options={
                "ordering": ["origen", "destino"],
                "verbose_name": "Ruta",
                "verbose_name_plural": "Rutas",
            },
        ),
        migrations.RenameField(
            model_name="ruta",
            old_name="distancia_km",
            new_name="precio_base",
        ),
        migrations.RenameField(
            model_name="ruta",
            old_name="tiempo_estimado_horas",
            new_name="dias_entrega",
        ),
        migrations.AddField(
            model_name="ruta",
            name="estado_tmp",
            field=models.IntegerField(
                choices=config.choices.EstadoGeneral.choices,
                default=config.choices.EstadoGeneral.ACTIVO,
            ),
        ),
        migrations.RunPython(migrar_rutas, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="ruta",
            name="estado",
        ),
        migrations.RemoveField(
            model_name="ruta",
            name="fecha_creacion",
        ),
        migrations.RemoveField(
            model_name="ruta",
            name="fecha_actualizacion",
        ),
        migrations.RemoveField(
            model_name="ruta",
            name="nombre",
        ),
        migrations.RenameField(
            model_name="ruta",
            old_name="estado_tmp",
            new_name="estado",
        ),
        migrations.AlterField(
            model_name="ruta",
            name="codigo",
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name="ruta",
            name="precio_base",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name="ruta",
            name="dias_entrega",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="ruta",
            name="estado",
            field=models.IntegerField(
                choices=config.choices.EstadoGeneral.choices,
                default=config.choices.EstadoGeneral.ACTIVO,
            ),
        ),
        migrations.AlterModelTable(
            name="ruta",
            table="rutas",
        ),
    ]
