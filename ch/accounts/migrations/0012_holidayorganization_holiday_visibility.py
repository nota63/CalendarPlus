# Generated by Django 5.1.2 on 2024-12-20 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_holidayorganization_allow_scheduling'),
    ]

    operations = [
        migrations.AddField(
            model_name='holidayorganization',
            name='holiday_visibility',
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
    ]