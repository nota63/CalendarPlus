import time
import schedule
import pytz
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from meet.models import Birthday
import pywhatkit as kit
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

class Command(BaseCommand):
    help = 'Send Birthday Wishes'

    def send_birthday_wishes(self):
  
        now = timezone.now()
        ist_now = now.astimezone(pytz.timezone('Asia/Kolkata'))  
        print(f"Current UTC Time: {now}")
        print(f"Current IST Time: {ist_now}")


        birthdays_today = Birthday.objects.filter(
            birthdate=ist_now.date(),  
        )

        # Debugging output to check the birthdays that are scheduled
        print(f"Birthdays to send wishes: {birthdays_today}")

        # Loop through the birthdays and send wishes via WhatsApp
        for birthday in birthdays_today:
            # Prepare message
            message = f"Happy Birthday, {birthday.name}! {birthday.message}"

            # Send message using pywhatkit
            self.send_whatsapp_message(birthday.phone_number, message, birthday.scheduled_time)

    def send_whatsapp_message(self, phone_number, message, scheduled_time):
        try:
            scheduled_time_ist = scheduled_time.astimezone(pytz.timezone('Asia/Kolkata'))
            time_hour = scheduled_time_ist.hour
            time_minute = scheduled_time_ist.minute
            current_time = timezone.now().astimezone(pytz.timezone('Asia/Kolkata'))
            scheduled_time_obj = current_time.replace(hour=time_hour, minute=time_minute, second=0, microsecond=0)

            if scheduled_time_obj < current_time:
                scheduled_time_obj = scheduled_time_obj + timedelta(days=1)

        
            time_diff = (scheduled_time_obj - current_time).total_seconds()
            print(f"Time to send message: {time_diff} seconds")

 
            if time_diff > 0:
                time.sleep(time_diff) 
            kit.sendwhatmsg(phone_number, message, scheduled_time_obj.hour, scheduled_time_obj.minute)
            print(f"Message sent to {phone_number}: {message}")

            # notify the sender 

            html_message=render_to_string('meet/automate_wish.html',{'birthday_user':Birthday.user,
                                                                     'shceduled_time':Birthday.scheduled_time,
                                                                     'sent_to':Birthday.name
                                                                     
                                                                     })

            send_mail(
                subject="Birthday wish sent successfully",
                message=f"Successfully wished to {Birthday.name}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[Birthday.user.email],
                html_message=html_message,
                fail_silently=False

            )

        except Exception as e:
            print(f"Error sending message to {phone_number}: {e}")

    def schedule_jobs(self):
        schedule.every(1).minute.do(self.send_birthday_wishes)

        while True:
            schedule.run_pending()
            time.sleep(1)  

    def handle(self, *args, **kwargs):
        print("Scheduler started...")
        self.schedule_jobs()
