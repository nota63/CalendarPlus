# Generated by Django 5.1.2 on 2024-11-30 07:12

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auths', '0021_meets_creator'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='meets',
            name='participants',
            field=models.ManyToManyField(blank=True, null=True, related_name='meetings_participants', to=settings.AUTH_USER_MODEL),
        ),
    ]