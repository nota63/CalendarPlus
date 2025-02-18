import schedule
import threading
import time
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from conversation.models import Todo  
from django.conf import settings

class Command(BaseCommand):
    help = "Check and send reminders for pending todos"

    def send_reminder_email(self, todo):
        """Send reminder email to the user."""
        subject = f"Reminder: {todo.todo}"
        message = (
            f"Hello {todo.user.first_name},\n\n"
            f"This is a reminder for your task: **{todo.todo}**.\n"
            f"Due Date: {todo.due_date.strftime('%Y-%m-%d %H:%M') if todo.due_date else 'No due date'}\n"
            f"Priority: {todo.get_priority_display()}\n"
            f"Status: {todo.get_status_display()}\n\n"
            f"Please take necessary action.\n\n"
            f"Regards,\nYour Team"
        )
        recipient_list = [todo.user.email]

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  
            recipient_list,
            fail_silently=False,
        )

        self.stdout.write(self.style.SUCCESS(f"Reminder sent for {todo.todo}"))

    def check_reminders(self):
        """Check all todos and send reminders if the time matches."""
        self.stdout.write(self.style.NOTICE("Checking reminders..."))

        now_time = now()
        time_window = now_time + timedelta(minutes=1)  # Look ahead for next minute reminders

        todos = Todo.objects.filter(
            due_date__lte=time_window,
            status__in=["pending", "in_progress"]
        )

        for todo in todos:
            if todo.reminder == "Before 10 minutes" and todo.due_date - timedelta(minutes=10) <= now_time:
                self.send_reminder_email(todo)
            elif todo.reminder == "Before 20 minutes" and todo.due_date - timedelta(minutes=20) <= now_time:
                self.send_reminder_email(todo)
            elif todo.reminder == "Before an hour" and todo.due_date - timedelta(hours=1) <= now_time:
                self.send_reminder_email(todo)

    def run_scheduler(self):
        """Schedule the reminder check every minute."""
        schedule.every(1).minutes.do(self.check_reminders)

        while True:
            schedule.run_pending()
            time.sleep(60)

    def handle(self, *args, **kwargs):
        """Run the command in a separate thread."""
        self.stdout.write(self.style.SUCCESS("Starting reminder checker..."))
        
        thread = threading.Thread(target=self.run_scheduler, daemon=True)
        thread.start()

        # Keep the command running
        while True:
            time.sleep(60)
