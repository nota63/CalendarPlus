# Generated by Django 5.1.5 on 2025-02-03 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0002_organizationhide_notify_members'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationhide',
            name='hide_on_sundays_and_holidays',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
