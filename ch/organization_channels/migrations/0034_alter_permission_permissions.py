# Generated by Django 5.1.5 on 2025-01-28 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization_channels', '0033_alter_permission_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='permissions',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
