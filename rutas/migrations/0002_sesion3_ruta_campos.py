# Generated manually for Sesion 3 ORM

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import migrations, models

import config.choices


class Migration(migrations.Migration):
    dependencies = [
        ("rutas", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="ruta",
            table="rutas_ruta",
        ),
        migrations.AlterField(
            model_name="ruta",
            name="distancia_km",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=8,
                validators=[MinValueValidator(Decimal("0.01"))],
            ),
        ),
        migrations.AlterField(
            model_name="ruta",
            name="estado",
            field=models.CharField(
                choices=config.choices.EstadoGeneral.choices,
                default=config.choices.EstadoGeneral.ACTIVO,
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="ruta",
            name="tiempo_estimado_horas",
            field=models.PositiveIntegerField(),
        ),
    ]
