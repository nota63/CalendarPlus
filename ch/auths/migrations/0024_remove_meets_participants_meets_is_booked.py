# Generated by Django 5.1.2 on 2024-11-30 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auths', '0023_availability_is_booked'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meets',
            name='participants',
        ),
        migrations.AddField(
            model_name='meets',
            name='is_booked',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]