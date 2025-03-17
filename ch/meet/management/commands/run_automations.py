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
from django.utils.timezone import localtime
from datetime import datetime
from group_tasks.models import CalPoints
from django.shortcuts import redirect, get_object_or_404


# IMPLEMENT THE COMMAND
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
        """Fetches and processes automation tasks while preventing duplicate executions per task."""
        self.stdout.write(self.style.SUCCESS("🔄 Running automation tasks..."))

        automations = AutomationTask.objects.all()

        for automation in automations:
            try:
                tasks = Task.objects.filter(assigned_to=automation.user)

                for task in tasks:
                    user = automation.user
                    group = automation.group
                    organization = automation.organization

                    # 🚀 Automation Conditions

                   # 1️⃣ **Send Welcome Text** (Only at 6 AM)
                    current_time = localtime().strftime("%H:%M")  # Get local time in HH:MM format

                    if automation.send_welcome_text and not task.welcome_text_sent and current_time == "06:00":
                        subject = "Good Morning! Wishing You a Productive Day Ahead 🌟"
                        message = (
                             f"Dear {task.created_by.username},\n\n"
                             f"Wishing you a wonderful and productive day ahead! May your tasks unfold smoothly, "
                             f"and your efforts bring success and fulfillment. If there's anything you need, feel free to reach out.\n\n"
                             f"Have a fantastic day!\n\n"
                             f"Best Regards,\n"
                             f"Wish by {task.assigned_to.username}\n  Task:{task.title},\n"
                             f"{organization.name} Team"
                               )

                        from_email = settings.DEFAULT_FROM_EMAIL
                        recipient_list = [task.created_by.email]
                        send_mail(subject, message, from_email, recipient_list)

                        # ✅ Mark as sent
                        task.welcome_text_sent = True
                        task.save()

                    self.stdout.write(self.style.SUCCESS(f"✅ Processed automations for task: {task.title}"))

                    # 2️⃣ **Send Submission Request to Assigned User if Task is Complete**
                    if automation.send_submission_request_after_completion:
                        if task.progress == 100 and task.status != "pending_approval" and not task.submission_request_sent:
                            task.status = "pending_approval"
                            task.submission_request_sent = True  # ✅ Mark task as processed
                            task.save()

                            subject = "Task Submission Awaiting Your Approval ✅"
                            message = (
                                f"Hello {task.created_by.username},\n\n"
                                f"Your task has been marked as complete and is now pending approval. Here are the details:\n\n"
                                f"📌 **Task:** {task.title}\n"
                                f"📅 **Deadline:** {task.deadline}\n"
                                f"⚡ **Priority:** {task.priority}\n\n"
                                f"📂 **Workspace:** {organization.name}\n"
                                f"👥 **Group:** {group.name}\n\n"
                                f"Please review the task and approve it via your dashboard.\n\n"
                                f"Thank you for your hard work!\n\n"
                                f"Best regards,\n"
                                f"Team CalendarPlus"
                            )

                            from_email = settings.DEFAULT_FROM_EMAIL
                            recipient_list = [task.created_by.email]  # 💡 Send email to `task.assigned_to`

                            send_mail(subject, message, from_email, recipient_list)

                    self.stdout.write(self.style.SUCCESS(f"✅ Processed automations for task: {task.title}"))


                    # SEND PROGRESS UPDATE TO MANAGER IF ENABLED
                    if automation.progress_update:
                        if task.progress and not task.progress_update_sent:
                            task.progress_update_sent=True
                            task.save()

                            subject=f'Progress Update Task: {task.title}'
                            message=(
                                f'Hello {task.created_by.username}\n'
                                f'We noticed One of your task you assigned to {task.assigned_to.username} Has Been progressed forward\n'
                                f'We thought will let you know about because the task is moving forward to be completed\n'
                                f'Below are the task & Workspace details you can read\n'
                                f'Task: {task.title}\n'
                                f'Deadline: {task.deadline}\n'
                                f'Priority:{task.priority}\n'
                                f'The task progress currently is {task.progress}%\n'
                                f'Workspace: {organization.name}\n'
                                f'Group: {group.name}\n'
                                f'Thank you\n'
                                f'Team CalendarPlus'
                            )
                            from_email=settings.DEFAULT_FROM_EMAIL
                            recipient_list=[task.created_by.email]

                            send_mail(subject, message, from_email, recipient_list)
                    self.stdout.write(self.style.SUCCESS(f"✅ Progress update sent : {task.title}"))

                    # SEND GREETING AFTER APPROVAL
                    if automation.send_greeting_after_approval:
                        if task.status == 'completed' and not task.after_approval_greeting_sent:
                            task.after_approval_greeting_sent=True
                            task.save()
                            # send greeting after approval
                            subject=f'Thank You {task.created_by.username} For My Task Approval'
                            message = (
                               f'Dear {task.created_by.username},\n\n'
                               f'I sincerely appreciate your time and effort in reviewing and approving my task submission. '
                               f'Your approval of the task **"{task.title}"** means a lot to me, and I am grateful for the opportunity to contribute effectively to our team.\n\n'
    
                               f'Here are the details of the approved task:\n\n'
                               f'🔹 **Task Title:** {task.title}\n'
                               f'📅 **Deadline:** {task.deadline}\n'
                               f'⚡ **Priority:** {task.priority}\n'
                               f'📌 **Status:** Approved & Completed ✅\n\n'

                               f'I am truly pleased that you found my work valuable, and I am eager to continue making meaningful contributions. '
                               f'Working on this task has been an enriching experience, and I look forward to taking on more challenges.\n\n'
    
                                f'### **Project Details:**\n'
                                f'🏢 **Organization:** {organization.name}\n'
                                f'👥 **Group:** {group.name}\n\n'
    
                                f'Thank you once again for your support and guidance. If there’s anything else I can improve or any feedback you’d like to share, '
                                f'please feel free to let me know.\n\n'
    
                                f'Looking forward to working on more projects together!\n\n'
    
                                f'Best Regards,\n'
                                f'{task.assigned_to.username}'
                            )
                            from_email=settings.DEFAULT_FROM_EMAIL
                            recipient_list=[task.created_by.email]

                            # send the email
                            send_mail(subject, message, from_email, recipient_list)

                    self.stdout.write(self.style.SUCCESS(f"✅ After approval Greeting Sent: {task.title}"))

                    # notify task creator after completion
                    if automation.notify_task_creator_on_completion:
                        if task.status == 'completed' and not task.after_completion_notification_sent:
                            task.after_completion_notification_sent = True
                            task.save()

                            # prepare the message
                            # Prepare the message
                            subject = f"🎯 Task Completion Notification: {task.title}"

                            message = (
                               f"Hello {task.created_by.username},\n\n"
                               f"We are delighted to inform you that the task **'{task.title}'** has been successfully completed.\n\n"
                               f"📌 **Task Details:**\n"
                               f"   - **Title:** {task.title}\n"
                               f"   - **Description:** {task.description}\n"
                               f"   - **Deadline:** {task.deadline}\n"
                               f"   - **Priority:** {task.priority}\n"
                               f"   - **Status:** Pending Approval ✅\n"
                               f"\n"
                               f"👨‍💻 **Assigned To:** {task.assigned_to.username}\n"
                               f"🏢 **Organization:** {task.organization.name}\n"
                               f"👥 **Group:** {task.group.name}\n\n"
                               f"The task has been successfully worked on, reaching its final stage. "
                               f"It is now ready for the next steps as needed. "
                               f"Feel free to access the details and take further actions through your dashboard.\n\n"
                               f"Thank you for your continued support and collaboration!\n\n"
                               f"Best Regards,\n"
                               f"✨ **Team {task.organization.name}**"
                             )
                            from_email= settings.DEFAULT_FROM_EMAIL
                            recipient_list=[task.created_by.email]
                            # send the email
                            send_mail(subject, message, from_email, recipient_list)

                    self.stdout.write(self.style.SUCCESS(f"✅ After completion Notification Sent Sent: {task.title}"))

                    # Escalate If Not Completed - Report to the Manager and - 5 Calpoints
                    # 🚨 Escalate If Not Completed - Report to Manager & Deduct 5 Calpoints
                    if automation.escalate_if_not_completed:
                      # Check if the task deadline has passed, task is NOT completed, and escalation action hasn't been taken
                         if task.deadline.date() <= datetime.now().date() and task.status != "completed" and not task.escalate_if_not_completed_action:
                              subject_created_by = f"⚠️ Urgent: Task '{task.title}' is Overdue!"
                              message_created_by = (
                              f"Dear {task.created_by.username},\n\n"
                              f"The task **'{task.title}'** assigned to **{task.assigned_to.username}** in **{task.organization.name}** "
                              f"was due on **{task.deadline.strftime('%Y-%m-%d')}**, but it has **not been completed** yet.\n\n"
                              f"As the task creator, you may consider the following actions:\n"
                              f"🔹 **Warn {task.assigned_to.username}** about the delay.\n"
                              f"🔹 **Reassign the task** to another member of **{task.organization.name}**.\n"
                              f"🔹 **Set a new deadline** if needed.\n\n"
                              f"📂 **Group:** {task.group.name}\n"
                              f"⚡ **Priority:** {task.priority}\n"
                              f"⏳ **Current Status:** {task.status}\n\n"
                              f"We have deducted 4 CalPoints from {task.assigned_to.username}'s account due to the task delay and transferred them to your account as compensation for overseeing the task's completion"
                              f"💡 To manage this task, please visit your dashboard.\n\n"
                              f"Best Regards,\n"
                              f"Team CalendarPlus"
                             )

                         from_email = settings.DEFAULT_FROM_EMAIL
                         recipient_list_created_by = [task.created_by.email]
        
                         # Send escalation warning email
                         send_mail(subject=subject_created_by, message=message_created_by, from_email=from_email, recipient_list=recipient_list_created_by)

                         # ✅ Mark task as escalated to prevent duplicate warnings
                        
                        #  send email to task.assigned_to about deadline missed and deducted the points
                         subject_user = "Task Deadline Missed – Points Deducted"
                         message_user = (
                              f"Hello {task.assigned_to.username},\n\n"
                              f"We noticed that the task **\"{task.title}\"** assigned to you under **{organization.name}** "
                              f"in the **{group.name}** workspace was not completed before the deadline (**{task.deadline}**).\n\n"
                              f"As a result, **4 CalPoints have been deducted from your account** and transferred to {task.assigned_to.username}'s Account** as per the organization's task compliance policy. "
                              f"Please ensure better time management in the future to avoid deductions.\n\n"
                              f"📌 **Task Details:**\n"
                              f"   - **Title:** {task.title}\n"
                              f"   - **Deadline:** {task.deadline}\n"
                              f"   - **Priority:** {task.priority}\n"
                              f"   - **Workspace:** {organization.name}\n"
                              f"   - **Group:** {group.name}\n\n"
                              f"If you need any assistance or have any concerns, feel free to reach out.\n\n"
                              f"Best Regards,\n"
                              f"Team CalendarPlus"
                            )
                         from_email=settings.DEFAULT_FROM_EMAIL
                         recipient_list_user=[task.assigned_to.email]
                         send_mail(subject=subject_user,message=message_user,from_email=from_email,recipient_list=recipient_list_user)


                         #🔹 Deduct 4 CalPoints from the task.assigned_to's account
                         # 🔹 Get user's CalPoints (Use .filter().first() to prevent errors)
                         calpoints = CalPoints.objects.filter(user=task.assigned_to, organization=organization).first()

                         if not calpoints or calpoints.points < 4:
                        # 🚨 User has insufficient CalPoints or no CalPoints record exists

                        # 🔹 Remove user from organization
                               profile = get_object_or_404(Profile, user=task.assigned_to, organization=organization)
                               profile.organization = None  # ❌ Remove user from the organization
                               profile.save()

                               # 🔹 Send removal notification to the user
                               subject = "Account Action: Removal from Organization"
                               message = (
                                        f"Dear {task.assigned_to.username},\n\n"
                                        f"We regret to inform you that due to missing the task deadline and insufficient CalPoints, "
                                        f"you have been removed from **{organization.name}**.\n\n"
                                        f"Your performance was reviewed, and your balance fell below the required threshold. "
                                        f"As a result, your access to the organization has been revoked.\n\n"
                                        f"If you have any concerns or believe this action was taken in error, please contact the administrator.\n\n"
                                        f"Best regards,\n"
                                        f"{organization.name} Team"
                                       )
                               send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [task.assigned_to.email])

                                # 🔹 Notify the manager about the removal
                               subject_manager = f"User {task.assigned_to.username} Removed from {organization.name} Due to Missed Deadline & Insufficient CalPoints"
                               message_manager = (
                                      f"Dear {task.created_by.username},\n\n"
                                      f"We would like to inform you that **{task.assigned_to.username}** has been removed from **{organization.name}** "
                                      f"due to failure to complete the assigned task (**{task.title}**) by the deadline (**{task.deadline}**), "
                                      f"combined with insufficient CalPoints in their account to cover the penalty.\n\n"
                                      f"As per our workflow, CalPoints are deducted when deadlines are missed to ensure accountability. "
                                      f"Since their balance was too low, they have been automatically removed from the organization.\n\n"
                                      f"If you believe this action was taken in error or wish to reinstate them, you may invite them back from your dashboard.\n\n"
                                      f"Let us know if you need any further assistance.\n\n"
                                      f"Best Regards,\n"
                                      f"Team CalendarPlus"
                                      )
                               send_mail(subject_manager, message_manager, settings.DEFAULT_FROM_EMAIL, [task.created_by.email])

                         else:
                             # ✅ Deduct 4 CalPoints if the user has enough
                            calpoints.points -= 4
                            calpoints.save()

                            # 🔹 Transfer 4 CalPoints to the manager's account (task.created_by)
                            calpoints_manager, created = CalPoints.objects.get_or_create(
                            user=task.created_by, organization=organization, group=group, task=task,
                            defaults={'points': 0}  # If no record exists, create one with 0 points
                            )

                            calpoints_manager.points += 4
                            calpoints_manager.save()

                            # 🔹 Notify manager about CalPoints transfer
                            subject_transfer = f"CalPoints Transfer Notification - {task.assigned_to.username}"
                            message_transfer = (
                                 f"Dear {task.created_by.username},\n\n"
                                  f"We have successfully transferred **4 CalPoints** from **{task.assigned_to.username}** to your account "
                                 f"as compensation for the missed deadline of the task **{task.title}**.\n\n"
                                 f"This ensures fairness and accountability in task management. Keep up the great work!\n\n"
                                 f"Best Regards,\n"
                                 f"Team CalendarPlus"
                                )
                            send_mail(subject_transfer, message_transfer, settings.DEFAULT_FROM_EMAIL, [task.created_by.email])

                              # change task settings
                            task.escalate_if_not_completed_action = True
                            task.save()


                        

                    self.stdout.write(self.style.WARNING(f"⚠️ Escalation triggered for overdue task: {task.title}"))


            except Exception as e:
                self.stderr.write(self.style.ERROR(f"❌ Error processing automation: {str(e)}"))

        self.stdout.write(self.style.SUCCESS("🎯 All automations processed successfully!"))
