import threading
import time
import schedule
import logging
import datetime
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from group_tasks.models import TaskReminder, Task

# Setup logging for debugging
logging.basicConfig(
    filename="task_reminders.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class TaskReminderService:
    """Handles scheduling, sending, and logging task reminders."""
    
    def __init__(self):
        self.running = True
        self.lock = threading.Lock()

    def get_pending_reminders(self):
        """Fetch reminders that are due and not sent."""
        return TaskReminder.objects.filter(
            reminder_time__lte=now(),
            is_sent=False,
            is_cancelled=False,
        )

    def send_reminder(self, reminder):
        """Send the reminder based on notification type."""
        try:
            task = reminder.task
            assignee = task.assigned_to
            creator = task.created_by
            subject = f"🔔 Reminder: {task.title} - {task.organization.name}"
            message = f"""
            Organization: {task.organization.name}
            Group: {task.group.name if task.group else 'N/A'}
            Task: {task.title}
            Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M')}
            Priority: {reminder.priority}
            """
            
            # Send email
            if reminder.notification_type == "email":
                recipients = [creator.email, assignee.email] if assignee else [creator.email]
                send_mail(subject, message, "no-reply@calendarplus.com", recipients)
                logging.info(f"📧 Email reminder sent for {task.title} to {recipients}")

            # Send in-app notification (Simulated)
            elif reminder.notification_type == "in_app":
                logging.info(f"📲 In-app reminder triggered for {task.title}")

            # Push notification (Simulated)
            elif reminder.notification_type == "push":
                logging.info(f"🚀 Push notification sent for {task.title}")

            # Webhook (Simulated)
            elif reminder.notification_type == "webhook":
                logging.info(f"🌍 Webhook triggered for {task.title}")

            # Mark reminder as sent
            reminder.is_sent = True
            reminder.save()
            logging.info(f"✅ Reminder marked as sent: {task.title}")

        except Exception as e:
            logging.error(f"❌ Error sending reminder for {reminder.task.title}: {e}")

    def process_reminders(self):
        """Fetch and process reminders every minute."""
        with self.lock:
            reminders = self.get_pending_reminders()
            logging.info(f"🔍 Found {len(reminders)} pending reminders.")

            for reminder in reminders:
                self.send_reminder(reminder)

    def start_scheduler(self):
        """Run the scheduler every minute."""
        schedule.every(1).minutes.do(self.process_reminders)

        while self.running:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds

    def stop(self):
        """Stop the scheduler."""
        self.running = False


class Command(BaseCommand):
    help = "Runs the task reminder scheduler"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("🚀 Task Reminder Service Started!"))

        reminder_service = TaskReminderService()

        # Start the scheduler in a separate thread
        thread = threading.Thread(target=reminder_service.start_scheduler)
        thread.start()

        # Keep the command running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n🛑 Stopping Task Reminder Service..."))
            reminder_service.stop()
            thread.join()
            self.stdout.write(self.style.SUCCESS("✅ Task Reminder Service Stopped!"))
