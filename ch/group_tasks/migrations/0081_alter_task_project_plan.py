# Generated by Django 5.1.6 on 2025-03-30 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group_tasks', '0080_alter_task_project_plan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='project_plan',
            field=models.TextField(blank=True, null=True),
        ),
    ]
