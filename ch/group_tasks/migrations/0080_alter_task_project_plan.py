# Generated by Django 5.1.6 on 2025-03-30 08:34

import django_quill.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group_tasks', '0079_alter_issueroom_files'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='project_plan',
            field=django_quill.fields.QuillField(blank=True, null=True),
        ),
    ]
