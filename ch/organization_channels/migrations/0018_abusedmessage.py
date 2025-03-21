# Generated by Django 5.1.5 on 2025-01-22 18:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0044_remove_organization_company_holidays'),
        ('organization_channels', '0017_alter_activitychannel_action_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AbusedMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_content', models.TextField(help_text='Content of the abused message')),
                ('flagged_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp when the message was flagged')),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='abused_messages', to='organization_channels.channel')),
                ('flagged_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='flagged_abused_messages', to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='abused_messages', to='accounts.organization')),
            ],
            options={
                'verbose_name': 'Abused Message',
                'verbose_name_plural': 'Abused Messages',
                'ordering': ['-flagged_at'],
            },
        ),
    ]
