# Generated by Django 5.1.6 on 2025-04-04 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0006_alter_premiumplan_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='premiumplan',
            name='name',
            field=models.CharField(choices=[('starter', 'Starter'), ('business+', 'Business +'), ('enterprise_grid', 'Enterprise Grid')], max_length=50, unique=True),
        ),
    ]
