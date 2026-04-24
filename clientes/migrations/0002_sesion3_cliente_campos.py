# Generated manually for Sesion 3 ORM

from django.db import migrations, models

import config.choices


class Migration(migrations.Migration):
    dependencies = [
        ("clientes", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="cliente",
            table="clientes_cliente",
        ),
        migrations.AddField(
            model_name="cliente",
            name="tipo_documento",
            field=models.CharField(
                choices=config.choices.TipoDocumento.choices,
                default=config.choices.TipoDocumento.DNI,
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="cliente",
            name="numero_documento",
            field=models.CharField(
                default="00000000",
                max_length=20,
                unique=True,
            ),
            preserve_default=False,
        ),
    ]
