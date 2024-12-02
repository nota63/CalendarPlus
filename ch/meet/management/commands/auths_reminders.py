import schedule
import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from auths.models import Reminder, Meets
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

        # Convert current time to IST
        ist_now = now.astimezone(pytz_timezone('Asia/Kolkata'))

        # Determine the reminder time range (send reminders 2 minutes before the scheduled time)
        reminder_start_time = ist_now
        reminder_end_time = ist_now + timedelta(minutes=2)

        # Fetch reminders that fall within the reminder time range for today
        reminders = Reminder.objects.filter(
            reminder_time__date=now.date(),
            reminder_time__time__range=(reminder_start_time.time(), reminder_end_time.time())
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
                'creator': meeting.creator.username,  # meeting creator
                'title': meeting.title,
                'day_of_week': meeting.day_of_week,
                'start_time': meeting.start_time,
                'end_time': meeting.end_time,
                'link': meeting.meeting_link,
                'user_email': user.email,
                'creator_email': meeting.creator.email
            }

            # Prepare the email content for the user
            html_message_user = render_to_string('calendar+/custom_user.html', context)
            try:
                user_subject = f"Meeting Reminder: {meeting.title}"
                user_message = (
                    f"Dear {user.username},\n\n"
                    f"This is a reminder for your meeting titled '{meeting.title}' scheduled at {meeting.start_time}.\n"
                    f"Join your meeting here: {meeting.meeting_link}\n\n"
                    "Looking forward to your participation!"
                )

                # Send the reminder email to the user
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

            # Prepare the email content for the creator/admin
            html_message_creator = render_to_string('calendar+/custom_creator.html', context)
            try:
                creator_subject = f"Admin Notification: Meeting Reminder for {meeting.title}"
                creator_message = (
                    f"Hello {meeting.creator.username},\n\n"
                    f"This is a reminder for the meeting titled '{meeting.title}' scheduled at {meeting.start_time}.\n"
                    f"Participant: {user.username}\n"
                    f"Join link: {meeting.meeting_link}\n\n"
                    "Please ensure the meeting proceeds smoothly."
                )

                # Send the reminder email to the meeting creator/admin
                send_mail(
                    subject=creator_subject,
                    message=creator_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    html_message=html_message_creator,
                    recipient_list=[meeting.creator.email],
                )
                self.stdout.write(self.style.SUCCESS(f'Reminder sent to creator for meeting: {meeting.title}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error sending email to creator for meeting {meeting.title}: {e}'))

    def schedule_jobs(self):
        # Schedule the reminder job to run every minute
        schedule.every(1).minutes.do(self.send_reminders)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def handle(self, *args, **kwargs):
        # Start the scheduler in a separate thread
        thread = threading.Thread(target=self.schedule_jobs)
        thread.start()
        self.stdout.write(self.style.SUCCESS('Scheduler started...'))
