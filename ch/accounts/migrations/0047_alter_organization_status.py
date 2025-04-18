# Generated by Django 5.1.5 on 2025-02-01 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0046_organization_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='status',
            field=models.CharField(blank=True, choices=[('working_remotely', 'Working Remotely'), ('in_a_meeting', 'In A Meeting'), ('off_sick', 'Off Sick'), ('on_holiday', 'On Holiday')], max_length=100, null=True),
        ),
    ]
