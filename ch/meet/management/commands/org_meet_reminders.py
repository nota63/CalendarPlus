import schedule
import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import MeetingReminder, MeetingOrganization
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
    help = 'Send meeting reminders'

    def send_reminders(self):
        now = timezone.now()  # Get current time in UTC
        ist_now = now.astimezone(pytz_timezone('Asia/Kolkata'))  # Current time in IST

        # Fetch reminders based on meeting time
        reminders = MeetingReminder.objects.filter(
            reminder_datetime__lte=ist_now,  # Reminder time is before or exactly the current time
            reminder_datetime__gt=ist_now - timedelta(minutes=1)  # Reminder time is within the last minute before the meeting
        )

        print(f"Current UTC Time: {now}")
        print(f"Current IST Time: {ist_now}")
        print(f"Reminders Found: {reminders}")

        for reminder in reminders:
            meeting = reminder.meeting
            context = {
                'user': meeting.user.username,
                'invitee': meeting.invitee.username,
                'title': meeting.meeting_title,
                'date': meeting.meeting_date,
                'time': meeting.start_time,
                'link': meeting.meeting_link,
                'type': meeting.meeting_type,
                'user_email': meeting.user.email,
                'invitee_email': meeting.invitee.email
            }

            # Select the template based on the reminder style
            if reminder.reminder_style == 'minimalist':
                html_message = render_to_string('themed_templates/minimalistic.html', context)
            elif reminder.reminder_style == 'modern':
                html_message = render_to_string('themed_templates/modern.html', context)
            elif reminder.reminder_style == 'dark':
                html_message = render_to_string('themed_templates/dark.html', context)
            elif reminder.reminder_style == 'classic':
                html_message = render_to_string('themed_templates/classic.html', context)
            elif reminder.reminder_style == 'playful':
                html_message = render_to_string('themed_templates/playful.html', context)
            else:
                # Default to minimalist if the style is undefined
                html_message = render_to_string('themed_templates/minimalistic.html', context)

            # Check the reminder time
            if reminder.reminder_time == 0:
                # Reminder time is set to "on meeting time"
                reminder_time = meeting.meeting_date + timedelta(minutes=meeting.start_time.minute, hours=meeting.start_time.hour)
                if reminder_time <= ist_now <= reminder_time + timedelta(minutes=1):  # Send reminder exactly at the meeting time
                    self.send_reminder_email(meeting, html_message)
            else:
                reminder_time = meeting.meeting_date + timedelta(minutes=meeting.start_time.minute, hours=meeting.start_time.hour) - timedelta(minutes=reminder.reminder_time)
                if reminder_time <= ist_now <= reminder_time + timedelta(minutes=1):  # Send reminder before the meeting time
                    self.send_reminder_email(meeting, html_message)

    def send_reminder_email(self, meeting, html_message, reminder):
    # Check if the MeetingReminder user matches meeting.user or meeting.invitee
      if reminder.user == meeting.user:
        try:
            user_subject = f"Meeting Reminder: {meeting.meeting_title}"
            user_message = (
                f"Dear {meeting.user.username},\n\n"
                f"This is a reminder for your meeting titled '{meeting.meeting_title}' scheduled at {meeting.start_time}.\n"
                f"Join your meeting here: {meeting.meeting_link}\n\n"
                "Looking forward to your participation!"
            )

            send_mail(
                subject=user_subject,
                message=user_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                html_message=html_message,
                recipient_list=[meeting.user.email],
            )
            self.stdout.write(self.style.SUCCESS(f'Reminder sent to user for meeting: {meeting.meeting_title}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error sending email to user for meeting {meeting.meeting_title}: {e}'))

      if reminder.user == meeting.invitee:
        try:
            invitee_subject = f"Meeting Reminder: {meeting.meeting_title}"
            invitee_message = (
                f"Dear {meeting.invitee.username},\n\n"
                f"This is a reminder for your meeting titled '{meeting.meeting_title}' scheduled at {meeting.start_time}.\n"
                f"Join your meeting here: {meeting.meeting_link}\n\n"
                "Looking forward to your participation!"
            )

            send_mail(
                subject=invitee_subject,
                message=invitee_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                html_message=html_message,
                recipient_list=[meeting.invitee.email],
            )
            self.stdout.write(self.style.SUCCESS(f'Reminder sent to invitee for meeting: {meeting.meeting_title}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error sending email to invitee for meeting {meeting.meeting_title}: {e}'))

    def schedule_jobs(self):
        # Run every minute to check if a reminder needs to be sent
        schedule.every(1).minute.do(self.send_reminders)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def handle(self, *args, **kwargs):
        thread = threading.Thread(target=self.schedule_jobs)
        thread.start()
        self.stdout.write(self.style.SUCCESS('Scheduler started...'))
