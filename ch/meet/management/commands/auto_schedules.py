import time
import threading
import schedule
import logging
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from gui_apps.models import AutoSchedule
from accounts.models import MeetingOrganization
from django.db import transaction

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Command(BaseCommand):
    help = "Automatically schedules meetings based on recurrence rules every minute"

    def handle(self, *args, **kwargs):
        """Start the scheduling thread"""
        self.stdout.write(self.style.SUCCESS("🔄 Auto-scheduler started..."))

        # Run the scheduler in a separate thread
        thread = threading.Thread(target=self.run_scheduler, daemon=True)
        thread.start()

        # Keep the command running indefinitely
        while True:
            time.sleep(1)

    def run_scheduler(self):
        """Runs the scheduler continuously every minute"""
        schedule.every(1).minutes.do(self.safe_check_and_schedule_meetings)

        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logging.error(f"Scheduler encountered an error: {e}", exc_info=True)

    def safe_check_and_schedule_meetings(self):
        """Wrapper function to ensure safe execution"""
        try:
            self.check_and_schedule_meetings()
        except Exception as e:
            logging.error(f"Error in check_and_schedule_meetings: {e}", exc_info=True)

    def check_and_schedule_meetings(self):
        """Fetch pending meetings and schedule them"""
        now_time = now().time()
        today = now().date()

        pending_meetings = AutoSchedule.objects.filter(
            status=AutoSchedule.StatusChoices.PENDING
        )

        logging.info(f"🔍 Checking {pending_meetings.count()} pending meetings...")

        for schedule_entry in pending_meetings:
            meeting_time = schedule_entry.time
            should_schedule = self.should_schedule_today(schedule_entry)

            if should_schedule and meeting_time <= now_time:
                with transaction.atomic():
                    success = self.schedule_meeting(schedule_entry)
                    if success:
                        schedule_entry.status = AutoSchedule.StatusChoices.SCHEDULED
                        logging.info(f"✅ Scheduled Meeting: {schedule_entry.meeting_title} at {meeting_time}")
                    else:
                        schedule_entry.status = AutoSchedule.StatusChoices.FAILED
                        logging.warning(f"⚠️ Failed to schedule: {schedule_entry.meeting_title} at {meeting_time}")

                    schedule_entry.last_attempted_schedule = now()
                    schedule_entry.save()

    def should_schedule_today(self, schedule_entry):
        """Check if the meeting should be scheduled today based on recurrence"""
        today = now().date()

        recurrence_map = {
            "daily": True,
            "weekly": today.weekday() == 0,  # Monday
            "biweekly": today.weekday() == 0 and today.day % 14 == 0,
            "monthly": today.day == 1,  # 1st of every month
            "monday": today.weekday() == 0,
            "tuesday": today.weekday() == 1,
            "wednesday": today.weekday() == 2,
            "thursday": today.weekday() == 3,
            "friday": today.weekday() == 4,
            "custom": today == schedule_entry.custom_date,
        }

        return recurrence_map.get(schedule_entry.recurrence, False)

    def schedule_meeting(self, schedule_entry):
        """Creates the meeting instance if there's no conflict"""
        today = now().date()
        meeting_time = schedule_entry.time

        # Conflict check
        if schedule_entry.skip_if_busy:
            conflicts = MeetingOrganization.objects.filter(
                organization=schedule_entry.organization,
                meeting_date=today,
                start_time=meeting_time,
                status=MeetingOrganization.StatusChoices.SCHEDULED,
            ).exists()

            if conflicts:
                schedule_entry.conflict_detected = True
                logging.warning(f"🚫 Conflict detected for: {schedule_entry.meeting_title} at {meeting_time}")
                return False  # Skip scheduling

        # Create the meeting
        meeting = MeetingOrganization.objects.create(
            organization=schedule_entry.organization,
            user=schedule_entry.creator,
            meeting_title=schedule_entry.meeting_title,
            meeting_date=today,
            start_time=meeting_time,
            status=MeetingOrganization.StatusChoices.SCHEDULED,
        )

        meeting.participants.set(schedule_entry.scheduled_with.all())
        meeting.save()
        return True
