# Generated by Django 5.1.6 on 2025-04-04 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0002_premiumplan'),
    ]

    operations = [
        migrations.AddField(
            model_name='premiumplan',
            name='features',
            field=models.TextField(blank=True, help_text='List of features included in the plan', null=True),
        ),
    ]
