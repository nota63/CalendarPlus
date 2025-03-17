import schedule
import threading
import time
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from group_tasks.models import AutomationTask, Task
from accounts.models import Profile, Organization
from groups.models import Group

class Command(BaseCommand):
    help = "Continuously runs automation tasks every minute"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("🚀 Automation Scheduler Started..."))

        # Start the scheduler in a separate thread
        thread = threading.Thread(target=self.run_scheduler, daemon=True)
        thread.start()

        # Keep the command running
        while True:
            time.sleep(1)

    def run_scheduler(self):
        """Runs the automation tasks every minute."""
        schedule.every(1).minutes.do(self.process_automations)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def process_automations(self):
        """Fetches and processes automation tasks while preventing duplicate executions."""
        self.stdout.write(self.style.SUCCESS("🔄 Running automation tasks..."))

        automations = AutomationTask.objects.all()

        for automation in automations:
            try:
                task = automation.task  
                user = automation.user  
                group = automation.group  
                organization = automation.organization  

                # Prevent re-execution on the same day
                if automation.last_executed and automation.last_executed.date() == now().date():
                    continue  # Skip if it has already run today

                # 🚀 Automation Conditions (With Tracking)
                
                if automation.send_welcome_text:
                   subject = "Good Morning! Wishing You a Productive Day Ahead 🌟"
                   message = (
                      f"Dear {task.created_by.username},\n\n"
                      f"Wishing you a wonderful and productive day ahead! May your tasks unfold smoothly, "
                      f"and your efforts bring success and fulfillment. If there's anything you need, feel free to reach out.\n\n"
                      f"Have a fantastic day!\n\n"
                      f"Best Regards,\n"
                      f"{organization.name} Team"
                     )
    
                   from_email = settings.DEFAULT_FROM_EMAIL
                   recipient_list = [task.created_by.email]
                   send_mail(subject, message, from_email, recipient_list)
                   automation.last_executed = now()
                   automation.save()


                # submission request after completion
                if automation.send_submission_request_after_completion:
                   if task.progress == 100:
                      task.status = 'pending_approval'  # Corrected assignment
        
                      subject = "Task Submission Awaiting Your Approval ✅"
                      message = (
                         f"Hello {task.created_by.username},\n\n"
                         f"{task.assigned_to.username} has submitted a task for your approval. Below are the details:\n\n"
                         f"📌 **Task:** {task.title}\n"
                         f"📅 **Deadline:** {task.deadline}\n"
                         f"⚡ **Priority:** {task.priority}\n\n"
                         f"📂 **Workspace:** {organization.name}\n"
                         f"👥 **Group:** {group.name}\n\n"
                         f"Please review and approve the task at your earliest convenience via your dashboard.\n\n"
                         f"Thank you for your collaboration!\n\n"
                         f"Best regards,\n"
                         f"Team CalendarPlus"
                         )
        
                      from_email = settings.DEFAULT_FROM_EMAIL
                      recipient_list = [task.created_by.email]
        
                      send_mail(subject, message, from_email, recipient_list)
                      automation.last_executed = now()
                      automation.save()

                
                if automation.generate_summary_after_approval:
                    pass  # TODO: Generate summary after approval
                
                if automation.translate_in_english:
                    pass  # TODO: Translate task content into English
                
                if automation.progress_update:
                    pass  # TODO: Send progress updates
                
                if automation.send_greeting_after_approval:
                    pass  # TODO: Send greeting after approval
                
                if automation.notify_task_creator_on_completion:
                    pass  # TODO: Notify task creator when task is completed
                
                if automation.escalate_if_not_completed:
                    pass  # TODO: Escalate task if not completed on time
                
                if automation.remind_before_deadline:
                    pass  # TODO: Send a reminder before the deadline
                
                if automation.auto_assign_reviewer:
                    pass  # TODO: Auto-assign a reviewer
                
                if automation.log_activity_on_completion:
                    pass  # TODO: Log task completion activity
                
                if automation.assign_task_if_previous_completed:
                    pass  # TODO: Assign a new task if the previous one is completed
                
                self.stdout.write(self.style.SUCCESS(f"✅ Processed automations for task: {task.title}"))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"❌ Error processing task {automation.task.title}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS("🎯 All automations processed successfully!"))
