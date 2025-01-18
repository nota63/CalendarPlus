import schedule
import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from meet.models import Reminder
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import threading
import os
import django
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from django.template.loader import render_to_string


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ch.settings')
django.setup()
print("Django setup complete. INSTALLED_APPS:", settings.INSTALLED_APPS)
from pytz import timezone as pytz_timezone  


class Command(BaseCommand):
    help = 'Send reminders based on the Reminder model'

    def send_reminders(self):
        now = timezone.now()

        ist_now = now.astimezone(pytz_timezone('Asia/Kolkata'))

        reminder_start_time = ist_now
        reminder_end_time = ist_now + timedelta(minutes=2)

        reminders = Reminder.objects.filter(
            reminder_datetime__date=now.date(),
            reminder_datetime__time__range=(reminder_start_time.time(), reminder_end_time.time())
        )

        print(f"Current UTC Time: {now}")
        print(f"Current IST Time: {ist_now}")
        print(f"Reminder Start Time: {reminder_start_time}, Reminder End Time: {reminder_end_time}")
        print(f"Reminders Found: {reminders}")

        for reminder in reminders:
            meeting = reminder.meeting
            user = reminder.user

            context = {
                'user': user.username,
                'admin': meeting.admin.username,
                'title': meeting.title,
                'date': meeting.date,
                'time': meeting.time,
                'link': meeting.meeting_link,
                'type': meeting.meeting_type,
                'user_email': user.email,
                'admin_email': meeting.admin.email
            }

            html_message_user = render_to_string('meet/custom_user.html', context)
            html_message_admin = render_to_string('meet/custom_admin.html', context)
            try:
                user_subject = f"Meeting Reminder: {meeting.title}"
                user_message = (
                    f"Dear {user.username},\n\n"
                    f"This is a reminder for your meeting titled '{meeting.title}' scheduled at {meeting.time}.\n"
                    f"Join your meeting here: {meeting.meeting_link}\n\n"
                    "Looking forward to your participation!"
                )

                send_mail(
                    subject=user_subject,
                    message=user_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    html_message=html_message_user,
                    recipient_list=[user.email],
                )
                self.stdout.write(self.style.SUCCESS(f'Reminder sent to user for meeting: {meeting.title}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error sending email to user for meeting {meeting.title}: {e}'))
            try:
                admin_subject = f"Admin Notification: Meeting Reminder for {meeting.title}"
                admin_message = (
                    f"Hello Admin,\n\n"
                    f"This is a notification about the upcoming meeting titled '{meeting.title}' scheduled at {meeting.time}.\n"
                    f"User: {user.username}\n"
                    f"Join link: {meeting.meeting_link}\n\n"
                    "Please ensure the meeting proceeds smoothly."
                )

                send_mail(
                    subject=admin_subject,
                    message=admin_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    html_message=html_message_admin,
                    recipient_list=[meeting.admin.email],
                )
                self.stdout.write(self.style.SUCCESS(f'Reminder sent to admin for meeting: {meeting.title}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error sending email to admin for meeting {meeting.title}: {e}'))

    def schedule_jobs(self):
        schedule.every(1).minutes.do(self.send_reminders)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def handle(self, *args, **kwargs):
        thread = threading.Thread(target=self.schedule_jobs)
        thread.start()
        self.stdout.write(self.style.SUCCESS('Scheduler started...'))

