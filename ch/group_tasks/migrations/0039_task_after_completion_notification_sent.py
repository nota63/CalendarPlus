# Generated by Django 5.1.6 on 2025-03-17 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group_tasks', '0038_task_after_approval_greeting_sent'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='after_completion_notification_sent',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
