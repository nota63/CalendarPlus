# Generated by Django 5.1.2 on 2024-11-02 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meet', '0005_docs'),
    ]

    operations = [
        migrations.AddField(
            model_name='docs',
            name='task_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
