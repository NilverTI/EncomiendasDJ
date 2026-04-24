from django.db import migrations, models

import config.choices


def migrar_estado_clientes(apps, schema_editor):
    Cliente = apps.get_model("clientes", "Cliente")
    for cliente in Cliente.objects.all():
        cliente.estado_tmp = (
            config.choices.EstadoGeneral.ACTIVO
            if cliente.activo
            else config.choices.EstadoGeneral.DE_BAJA
        )
        cliente.save(update_fields=["estado_tmp"])


class Migration(migrations.Migration):
    dependencies = [
        ("clientes", "0002_sesion3_cliente_campos"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="cliente",
            options={
                "ordering": ["apellidos", "nombres"],
                "verbose_name": "Cliente",
                "verbose_name_plural": "Clientes",
            },
        ),
        migrations.RenameField(
            model_name="cliente",
            old_name="nombre",
            new_name="nombres",
        ),
        migrations.RenameField(
            model_name="cliente",
            old_name="apellido",
            new_name="apellidos",
        ),
        migrations.RenameField(
            model_name="cliente",
            old_name="tipo_documento",
            new_name="tipo_doc",
        ),
        migrations.RenameField(
            model_name="cliente",
            old_name="numero_documento",
            new_name="nro_doc",
        ),
        migrations.RenameField(
            model_name="cliente",
            old_name="fecha_creacion",
            new_name="fecha_registro",
        ),
        migrations.AddField(
            model_name="cliente",
            name="estado_tmp",
            field=models.IntegerField(
                choices=config.choices.EstadoGeneral.choices,
                default=config.choices.EstadoGeneral.ACTIVO,
            ),
        ),
        migrations.RunPython(migrar_estado_clientes, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="cliente",
            name="activo",
        ),
        migrations.RemoveField(
            model_name="cliente",
            name="ciudad",
        ),
        migrations.RenameField(
            model_name="cliente",
            old_name="estado_tmp",
            new_name="estado",
        ),
        migrations.AlterField(
            model_name="cliente",
            name="tipo_doc",
            field=models.CharField(
                choices=config.choices.TipoDocumento.choices,
                default=config.choices.TipoDocumento.DNI,
                max_length=3,
            ),
        ),
        migrations.AlterField(
            model_name="cliente",
            name="nro_doc",
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name="cliente",
            name="telefono",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name="cliente",
            name="email",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name="cliente",
            name="direccion",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="cliente",
            name="estado",
            field=models.IntegerField(
                choices=config.choices.EstadoGeneral.choices,
                default=config.choices.EstadoGeneral.ACTIVO,
            ),
        ),
        migrations.AlterModelTable(
            name="cliente",
            table="clientes",
        ),
    ]
