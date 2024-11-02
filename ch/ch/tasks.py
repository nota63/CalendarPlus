
from django.utils import timezone
from meet.models import Meeting
# from .views import send_meeting_reminder
from django.core.mail import send_mail
from django.conf import settings

from datetime import timedelta



def check_meetings_and_send_reminders():
    now = timezone.now()
    current_time = now.time()
    current_date = now.date()

    # Fetch meetings that are due to send reminders
    meetings = Meeting.objects.filter(
        date=current_date,
        time__range=(current_time - timedelta(minutes=1), current_time + timedelta(minutes=1))
    )

    # send the email reminder to the user and admin associated with this meeting
    for meeting in meetings:
        recipients = [meeting.user.email, meeting.admin.email]
        try:
            send_mail(
                subject=f"Meeting Reminder: {meeting.title}",
                message=f"Reminder for your meeting '{meeting.title}' scheduled at {meeting.time}. Join here: {meeting.meeting_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
            )
            print(f"Reminder sent for meeting: {meeting.title}")
        except Exception as e:
            print(f"Error sending email for meeting {meeting.title}: {e}")