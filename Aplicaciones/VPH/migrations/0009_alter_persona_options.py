# Generated by Django 4.2.5 on 2023-11-02 23:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VPH', '0008_alter_persona_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='persona',
            options={'permissions': [('can_view_persona', 'Can view persona'), ('can_change_persona', 'Can change persona'), ('can_add_persona', 'Can add persona'), ('can_delete_persona', 'Can delete persona')]},
        ),
    ]
