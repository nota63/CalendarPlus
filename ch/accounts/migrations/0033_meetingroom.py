# Generated by Django 5.1.2 on 2024-12-24 09:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0032_meetingnotes_delete_meetingnote'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MeetingRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_name', models.CharField(max_length=255, unique=True)),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.meetingorganization')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.organization')),
                ('participants', models.ManyToManyField(related_name='meeting_participants', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
