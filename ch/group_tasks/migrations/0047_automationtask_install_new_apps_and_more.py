# Generated by Django 5.1.6 on 2025-03-18 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group_tasks', '0046_task_log_completion_activity'),
    ]

    operations = [
        migrations.AddField(
            model_name='automationtask',
            name='install_new_apps',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='task_chaining_notification_sent',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
