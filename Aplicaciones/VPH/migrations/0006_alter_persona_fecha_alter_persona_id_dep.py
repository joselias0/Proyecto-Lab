# Generated by Django 4.2.5 on 2023-09-26 03:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('VPH', '0005_alter_persona_id_dep'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='fecha',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='persona',
            name='id_dep',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VPH.departamento'),
        ),
    ]