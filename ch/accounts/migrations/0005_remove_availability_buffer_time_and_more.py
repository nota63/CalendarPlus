# Generated by Django 5.1.2 on 2024-12-14 08:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_availability_organization'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='availability',
            name='buffer_time',
        ),
        migrations.RemoveField(
            model_name='availability',
            name='is_recurring',
        ),
        migrations.RemoveField(
            model_name='availability',
            name='meeting_duration',
        ),
    ]