import logging
import time
from datetime import datetime, time as datetime_time, timedelta
from threading import Event

import schedule
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone

from group_tasks.models import TaskReminder

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sends task reminders via email and handles recurring schedules"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting task reminder scheduler..."))
        self._run_scheduler()

    def _run_scheduler(self):
        """Runs the scheduler loop to check reminders every minute."""
        stop_event = Event()
        schedule.every(1).minutes.do(self._check_reminders)

        try:
            while not stop_event.is_set():
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nStopping scheduler..."))
            stop_event.set()
        except Exception as e:
            logger.critical(f"Scheduler crashed: {e}", exc_info=True)
            raise

    def _check_reminders(self):
        """Main method to process all active reminders."""
        try:
            self.stdout.write(f"Checking reminders at {timezone.now()}...")
            reminders = TaskReminder.objects.filter(
                notification_type="email",
                is_sent=False,
                is_cancelled=False,
            ).exclude(
                models.Q(snooze_until__gt=timezone.now())
            ).select_related(
                "task", "organization", "group", "created_by", "task__assigned_to"
            )

            for reminder in reminders:
                self._process_single_reminder(reminder)

        except Exception as e:
            logger.error(f"Error processing reminders: {e}", exc_info=True)

    def _process_single_reminder(self, reminder):
        """Processes an individual reminder with full error handling."""
        try:
            # Auto-cancel if task is completed
            if reminder.task.status == "Completed":
                reminder.is_cancelled = True
                reminder.save()
                self.stdout.write(f"Cancelled reminder {reminder.id} (task completed)")
                return

            # Handle recurring scheduling logic
            if self._is_recurring(reminder):
                self._handle_recurring_scheduling(reminder)

            # Send reminder if time is due
            if reminder.reminder_time and timezone.now() >= reminder.reminder_time:
                self._send_reminder_email(reminder)
                self._handle_post_send_actions(reminder)

        except Exception as e:
            logger.error(f"Error processing reminder {reminder.id}: {e}", exc_info=True)

    def _is_recurring(self, reminder):
        """Determines if a reminder has recurring settings."""
        return any([
            reminder.remind_assignee_every_morning,
            reminder.remind_assignee_every_evening,
            reminder.remind_every_x_days,
            reminder.remind_every_x_weeks,
            reminder.remind_every_x_months
        ])

    def _handle_recurring_scheduling(self, reminder):
        """Ensures recurring reminders have valid future schedule times."""
        needs_reschedule = (
            reminder.reminder_time is None or 
            reminder.reminder_time <= timezone.now()
        )

        if needs_reschedule:
            next_time = self._calculate_next_occurrence(reminder)
            if next_time:
                reminder.reminder_time = next_time
                reminder.save()
                self.stdout.write(f"Scheduled recurring reminder {reminder.id} for {next_time}")

    def _calculate_next_occurrence(self, reminder):
        """Calculates next trigger time based on recurrence rules."""
        now = timezone.localtime()
        current_date = now.date()
        current_time = now.time()

        if reminder.remind_assignee_every_morning:
            return self._next_time_of_day(current_date, current_time, 9, 0)
        elif reminder.remind_assignee_every_evening:
            return self._next_time_of_day(current_date, current_time, 18, 0)
        elif reminder.remind_every_x_days is not None:
            return self._add_interval(reminder.reminder_time, days=reminder.remind_every_x_days)
        elif reminder.remind_every_x_weeks is not None:
            return self._add_interval(reminder.reminder_time, weeks=reminder.remind_every_x_weeks)
        elif reminder.remind_every_x_months is not None:
            return self._add_interval(reminder.reminder_time, months=reminder.remind_every_x_months)
        return None

    def _next_time_of_day(self, current_date, current_time, hour, minute):
        """Calculates next occurrence for daily time-based reminders."""
        target_time = datetime_time(hour, minute)
        if current_time < target_time:
            next_datetime = datetime.combine(current_date, target_time)
        else:
            next_datetime = datetime.combine(
                current_date + timedelta(days=1), 
                target_time
            )
        return timezone.make_aware(next_datetime)

    def _add_interval(self, base_time, **kwargs):
        """Adds time interval to base_time with safe None handling."""
        if base_time is None:
            base_time = timezone.localtime()
        
        if "months" in kwargs:
            months = kwargs.pop("months")
            kwargs["days"] = months * 30  # Using model's 30-day month approximation
        
        return base_time + timedelta(**kwargs)

    def _send_reminder_email(self, reminder):
        """Handles email sending with proper templating and error handling."""
        try:
            context = self._build_email_context(reminder)
            recipients = self._get_recipients(reminder)

            if not recipients:
                logger.warning(f"No valid recipients for reminder {reminder.id}")
                return

            self._dispatch_email(
                subject=f"Reminder: {reminder.task.title}",
                context=context,
                recipients=recipients
            )
            self.stdout.write(f"Sent email for reminder {reminder.id}")

        except Exception as e:
            logger.error(f"Email failed for reminder {reminder.id}: {e}", exc_info=True)
            raise

    def _build_email_context(self, reminder):
        """Constructs email template context."""
        task = reminder.task
        return {
            "task_title": task.title,
            "priority": reminder.priority.upper(),
            "organization": reminder.organization.name if reminder.organization else "N/A",
            "group": reminder.group.title if reminder.group else "N/A",
            "created_by": reminder.created_by.get_full_name(),
            "assigned_to": task.assigned_to.get_full_name() if task.assigned_to else "Unassigned",
            "deadline": task.deadline.strftime("%Y-%m-%d %H:%M") if task.deadline else "Not specified",
            "details": task.description or "No additional details",
            "reminder_time": timezone.localtime(reminder.reminder_time).strftime("%Y-%m-%d %H:%M"),
        }

    def _get_recipients(self, reminder):
        """Extracts valid email recipients."""
        recipients = []
        if reminder.created_by.email:
            recipients.append(reminder.created_by.email)
        if reminder.task.assigned_to and reminder.task.assigned_to.email:
            recipients.append(reminder.task.assigned_to.email)
        return recipients

    def _dispatch_email(self, subject, context, recipients):
        """Sends actual email using Django's mail system."""
        send_mail(
            subject=subject,
            message=render_to_string("tasks/email/reminder.txt", context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            html_message=render_to_string("task/email/reminder_email.html", context),
            fail_silently=False,
        )

    def _handle_post_send_actions(self, reminder):
        """Updates reminder status and handles rescheduling."""
        reminder.is_sent = True
        reminder.save()

        if reminder.auto_reschedule and self._is_recurring(reminder):
            next_time = self._calculate_next_occurrence(reminder)
            if next_time:
                reminder.reminder_time = next_time
                reminder.is_sent = False
                reminder.save()
                self.stdout.write(f"Rescheduled reminder {reminder.id} for {next_time}")