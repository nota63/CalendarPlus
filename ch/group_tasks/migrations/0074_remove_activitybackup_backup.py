# Generated by Django 5.1.6 on 2025-03-27 04:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group_tasks', '0073_alter_activitybackup_backup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activitybackup',
            name='backup',
        ),
    ]
