# Generated by Django 5.1.6 on 2025-03-03 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_marketplace', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='miniapp',
            name='requirements',
            field=models.CharField(default='Windows 10 + Higher', max_length=255),
        ),
    ]
