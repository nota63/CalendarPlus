# Generated by Django 5.1.2 on 2024-12-14 07:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_remove_organization_current_project'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.CharField(blank=True, choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], max_length=10, null=True)),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('meeting_duration', models.PositiveIntegerField(blank=True, null=True)),
                ('buffer_time', models.PositiveIntegerField(blank=True, null=True)),
                ('is_recurring', models.BooleanField(blank=True, default=False, null=True)),
                ('is_booked', models.BooleanField(blank=True, default=False, null=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availabilities', to='accounts.organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availabilities', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
