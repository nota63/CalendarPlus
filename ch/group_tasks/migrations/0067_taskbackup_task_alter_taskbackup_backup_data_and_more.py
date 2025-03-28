# Generated by Django 5.1.6 on 2025-03-23 01:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0056_organization_created_by'),
        ('group_tasks', '0066_taskbackup'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='taskbackup',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='group_tasks.task'),
        ),
        migrations.AlterField(
            model_name='taskbackup',
            name='backup_data',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='taskbackup',
            name='backup_type',
            field=models.CharField(blank=True, choices=[('manual', 'Manual'), ('auto', 'Automatic')], default='manual', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='taskbackup',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='taskbackup',
            name='is_restored',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='taskbackup',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.organization'),
        ),
        migrations.AlterField(
            model_name='taskbackup',
            name='storage_location',
            field=models.CharField(blank=True, choices=[('database', 'Database'), ('file', 'File Storage')], default='database', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='taskbackup',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
