import schedule
import time
import pywhatkit
from django.core.management.base import BaseCommand
from django.utils import timezone
from meet.models import Birthday
from datetime import timedelta
import threading
import os
import django
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from django.conf import settings
from pytz import timezone as pytz_timezone  


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ch.settings')
django.setup()
print("Django setup complete. INSTALLED_APPS:", settings.INSTALLED_APPS)

class Command(BaseCommand):
    help = 'Send birthday wishes based on the Birthday model'

    def send_birthday_wishes(self):
        now = timezone.now()
        ist_now = now.astimezone(pytz_timezone('Asia/Kolkata'))
        birthday_start_time = ist_now
        birthday_end_time = ist_now + timedelta(minutes=2)

    
        birthdays = Birthday.objects.filter(
            scheduled_time__date=now.date(),
            scheduled_time__time__range=(birthday_start_time.time(), birthday_end_time.time())
        )

   
        print(f"Current UTC Time: {now}")
        print(f"Current IST Time: {ist_now}")
        print(f"Birthday Start Time: {birthday_start_time}, Birthday End Time: {birthday_end_time}")
        print(f"Birthdays Found: {birthdays}")

        # Send WhatsApp messages if any found
        for birthday in birthdays:
            user = birthday.user
            phone_number = birthday.phone_number
            message = birthday.message

          
            formatted_message = f"Happy Birthday {user.username}!\n\n{message}"

            try:
            
                scheduled_time_ist = birthday.scheduled_time.astimezone(pytz_timezone('Asia/Kolkata'))
                send_hour = scheduled_time_ist.hour
                send_minute = scheduled_time_ist.minute
                pywhatkit.sendwhatmsg(
                    f"+{phone_number}",  
                    formatted_message,   
                    send_hour,           
                    send_minute         
                )

                self.stdout.write(self.style.SUCCESS(f'Birthday message sent to {user.username} at {formatted_message}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error sending birthday message to {user.username}: {e}'))

    def schedule_jobs(self):
        # Schedule the send_birthday_wishes method to run every minute
        schedule.every(1).minutes.do(self.send_birthday_wishes)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def handle(self, *args, **kwargs):
        # Run the scheduler in a separate thread
        thread = threading.Thread(target=self.schedule_jobs)
        thread.start()
        self.stdout.write(self.style.SUCCESS('Scheduler started...'))
