# Generated by Django 5.1.2 on 2024-11-29 02:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auths', '0009_meet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meet',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auths.organization'),
        ),
    ]