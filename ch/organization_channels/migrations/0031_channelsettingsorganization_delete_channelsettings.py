# Generated by Django 5.1.5 on 2025-01-26 13:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0044_remove_organization_company_holidays'),
        ('organization_channels', '0030_alter_channelsettings_allow_emoji_usage_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChannelSettingsOrganization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allow_media_uploads', models.BooleanField(blank=True, default=True, null=True)),
                ('allow_codes', models.BooleanField(blank=True, default=False, null=True)),
                ('secure_from_unwanted_requests', models.BooleanField(blank=True, default=False, null=True)),
                ('allow_polls', models.BooleanField(blank=True, default=False, null=True)),
                ('allow_sharing_access_to_another_workspace', models.BooleanField(blank=True, default=True, null=True)),
                ('track_abusive_messages', models.BooleanField(blank=True, default=True, null=True)),
                ('allow_integrations', models.BooleanField(blank=True, default=False, null=True)),
                ('integration_choices', models.CharField(choices=[('Slack', 'slack'), ('Trello', 'trello'), ('Calendly', 'calendly')], max_length=100)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to='organization_channels.channel')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to='accounts.organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='ChannelSettings',
        ),
    ]
