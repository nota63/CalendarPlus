# Generated by Django 5.1.2 on 2024-12-25 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0039_remove_meetingnotes_emojis_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meetingnotes',
            name='voice_message',
        ),
        migrations.AddField(
            model_name='meetingnotes',
            name='attachments',
            field=models.FileField(blank=True, null=True, upload_to='meeting_notes_attachments/'),
        ),
    ]
