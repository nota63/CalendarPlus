# Generated by Django 5.1.2 on 2024-11-30 17:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auths', '0024_remove_meets_participants_meets_is_booked'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reminder_time', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reminders', to='auths.meets')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reminders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['reminder_time'],
            },
        ),
    ]
