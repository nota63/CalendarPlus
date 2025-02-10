import schedule
import time
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from organizations.models  import RecurringMeeting

class Command(BaseCommand):
    help = "Schedules and creates recurring meetings automatically"

    def create_meeting_instance(self, meeting, new_date):
        """Create a new meeting instance if it doesn't already exist for that date."""
        if not RecurringMeeting.objects.filter(start_date=new_date, created_by=meeting.created_by).exists():
            RecurringMeeting.objects.create(
                organization=meeting.organization,
                type=meeting.type,
                recurrence_type=meeting.recurrence_type,
                start_date=new_date,
                end_date=meeting.end_date,
                remind_before=meeting.remind_before,
                send_email_reminder=meeting.send_email_reminder,
                send_push_notification=meeting.send_push_notification,
                exclude_dates=meeting.exclude_dates,
                creator=meeting.creator,
                created_by=meeting.created_by,
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Created meeting for {new_date}"))

    def process_recurring_meetings(self):
        """Fetch all recurring meetings and generate new ones if necessary."""
        today = date.today()
        meetings = RecurringMeeting.objects.filter(start_date__lte=today)

        for meeting in meetings:
            if meeting.end_date and today > meeting.end_date:
                continue  # Skip expired recurring meetings

            # Skip excluded dates
            if meeting.exclude_dates and today.strftime("%Y-%m-%d") in meeting.exclude_dates:
                continue  

            if meeting.recurrence_type == "daily":
                next_date = meeting.start_date + timedelta(days=1)
            elif meeting.recurrence_type == "weekly":
                next_date = meeting.start_date + timedelta(weeks=1)
            elif meeting.recurrence_type == "monthly":
                next_date = meeting.start_date.replace(
                    month=meeting.start_date.month + 1 if meeting.start_date.month < 12 else 1,
                    year=meeting.start_date.year if meeting.start_date.month < 12 else meeting.start_date.year + 1
                )
            elif meeting.recurrence_type == "yearly":
                next_date = meeting.start_date.replace(year=meeting.start_date.year + 1)
            elif meeting.recurrence_type == "custom" and meeting.custom_days:
                next_date = today + timedelta(days=min(meeting.custom_days, key=lambda d: abs(d - today.weekday())))
            else:
                continue  # Unknown type

            self.create_meeting_instance(meeting, next_date)

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("🚀 Starting recurring meeting scheduler..."))

        # Run every minute
        schedule.every(1).minutes.do(self.process_recurring_meetings)

        while True:
            schedule.run_pending()
            time.sleep(60)  # Wait 1 minute before checking again
