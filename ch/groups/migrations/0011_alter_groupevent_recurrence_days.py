# Generated by Django 5.1.6 on 2025-04-01 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0010_groupactivity_event_alter_groupactivity_action_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupevent',
            name='recurrence_days',
            field=models.CharField(blank=True, help_text="Comma-separated days for weekly recurrence, e.g., 'Monday, Wednesday'.", max_length=50, null=True),
        ),
    ]
