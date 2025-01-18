# scheduler.py

import schedule
import time
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ch.settings')
django.setup()

from django.core.management import call_command

def send_reminders():
    call_command('send_meeting_reminders')

# Schedule the task to run every minute
schedule.every(1).minutes.do(send_reminders)

while True:
    schedule.run_pending()
    time.sleep(1)
