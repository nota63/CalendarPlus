# Generated by Django 5.1.5 on 2025-01-23 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization_channels', '0019_message_is_pinned'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_starred',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='activitychannel',
            name='action_type',
            field=models.CharField(choices=[('MESSAGE', 'Message'), ('MENTION', 'Mention'), ('EMOJI', 'Emoji'), ('LINK', 'Link'), ('FILE_UPLOAD', 'File Upload'), ('JOIN', 'Join'), ('LEAVE', 'Leave'), ('DATA_EXPORT', 'Data export'), ('EXPLORE_STATISTICS', 'Explore statistics'), ('MESSAGES_DELETE', 'Messages delete'), ('MESSAGE_DELETE', 'Message_delete'), ('LINK_DELETE', 'Link delete'), ('MESSAGE_EDITED', 'Message edited'), ('LINK_EDITED', 'Link edited'), ('FILTERED_MESSAGES', 'Filtered messages'), ('BAN_USER', 'Ban user'), ('CHANNEL_ACCESS', 'Channel access'), ('SET_RETENTION_POLICY', 'Set retention policy'), ('PINNED_MESSAGE', 'Pinned message')], max_length=20),
        ),
    ]
