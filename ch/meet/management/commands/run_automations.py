
from datetime import datetime, time  
from django.utils import timezone
import schedule
import threading
import time
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from group_tasks.models import (AutomationTask, Task,TaskTimeTracking,TaskComment,TaskNote,AttachmentsTasksApp,SubTask,ActivityLog,TaskCompletionActivities,MeetingTaskQuery)
from accounts.models import Profile, Organization,Availability,MeetingOrganization
from groups.models import Group
from django.utils.timezone import localtime
from datetime import datetime
from group_tasks.models import CalPoints
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from app_marketplace.models import MiniApp, InstalledMiniApp
import logging
logger = logging.getLogger(__name__)  # Logger for debugging


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


                    # Remind before deadline notification
                    # Get today's date
                    today_date = timezone.now().date()

                    # Print task details
                    print(f"🔹 Checking reminders for task: {task.title} (Deadline: {task.deadline})")
                    print(f"🔹 Today's date: {today_date}")

                    # Reminder logic for 2 days before the deadline
                    if automation.remind_before_deadline:
                          print(f"🔹 Reminder setting is enabled ✅")
    
                          if task.status != "completed":
                               print(f"🔹 Task is still **pending** (Status: {task.status})")

                               # Reminder logic for 2 days before the deadline
                               if task.deadline and (task.deadline - timedelta(days=2)).date() == today_date:
                                   print(f"🔹 Task deadline is in **2 days** (Triggering first reminder)")

                                   if not task.reminder_before_2_days_sent:
                                        print(f"✅ First reminder **NOT** sent yet! Sending now...")

                                        subject = f"Reminder: Task '{task.title}' Deadline in 2 Days"
                                        message = (
                                             f"Dear {task.assigned_to.username},\n\n"
                                             f"This is a friendly reminder that your task **'{task.title}'** is due in **2 days** (Deadline: {task.deadline}).\n"
                                             f"Please make sure you're on track to complete it on time.\n\n"
                                             f"Let us know if you need assistance.\n\n"
                                             f"Best Regards,\n"
                                             f"Team {organization.name}"
                                                )
                
                                        try:
                                            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [task.assigned_to.email])
                                            print(f"✅ Email sent successfully to {task.assigned_to.email}")
                    
                                            # Mark reminder as sent
                                            task.reminder_before_2_days_sent = True
                                            task.save()
                                            print(f"✅ Task updated: reminder_before_2_days_sent = True")

                                        except Exception as e:
                                           print(f"❌ ERROR sending first reminder email: {e}")

                                   else:
                                      print(f"⚠️ First reminder already sent. Skipping...")

                               else:
                                   print(f"❌ Today is NOT 2 days before the deadline. No first reminder sent.")

                           
                               # Reminder logic for 1 day before the deadline
                               if task.deadline and (task.deadline - timedelta(days=1)).date() == today_date:
                                    print(f"🔹 Task deadline is **tomorrow** (Triggering final reminder)")

                                    if not task.reminder_before_1_day_sent:
                                         print(f"✅ Final reminder **NOT** sent yet! Sending now...")

                                         subject_1_day = f"Final Reminder: Task '{task.title}' Deadline Tomorrow!"
                                         message_1_day = (
                                               f"Dear {task.assigned_to.username},\n\n"
                                               f"This is your final reminder! Your task **'{task.title}'** is due **tomorrow** (Deadline: {task.deadline}).\n"
                                               f"Please ensure it is completed on time to avoid penalties.\n\n"
                                               f"Reach out if you need any support.\n\n"
                                               f"Best Regards,\n"
                                               f"Team {organization.name}"
                                                )
                
                                         try:
                                             send_mail(subject_1_day, message_1_day, settings.DEFAULT_FROM_EMAIL, [task.assigned_to.email])
                                             print(f"✅ Final reminder email sent successfully to {task.assigned_to.email}")

                                             # Mark reminder as sent
                                             task.reminder_before_1_day_sent = True
                                             task.save()
                                             print(f"✅ Task updated: reminder_before_1_day_sent = True")

                                         except Exception as e:
                                              print(f"❌ ERROR sending final reminder email: {e}")

                                         # 🔹 Notify manager as well
                                         subject_manager = f"Task Pre-Deadline Reminder"
                                         message_manager = f"Hello Manager,\n\nThe task **'{task.title}'** assigned to {task.assigned_to.username} has an approaching deadline.\n\nPlease ensure all necessary actions are taken.\n\nBest,\n{organization.name}"
                
                                         try:
                                             send_mail(subject_manager, message_manager, settings.DEFAULT_FROM_EMAIL, [task.created_by.email])
                                             print(f"✅ Manager notified via email: {task.created_by.email}")

                                         except Exception as e:
                                             print(f"❌ ERROR sending manager notification: {e}")

                                    else:
                                        print(f"⚠️ Final reminder already sent. Skipping...")

                               else:
                                   print(f"❌ Today is NOT 1 day before the deadline. No final reminder sent.")

                          else:
                             print(f"⚠️ Task is already completed. No reminders needed.")

                    else:
                        print(f"❌ Reminder setting is **disabled**. No emails will be sent.")

                    print(f"✅ Reminder check completed for task: {task.title}")

                    # ** Handle Auto Task reviewer assignment
                    # Handle Auto Task reviewer assignment
                    print("🔍 Checking Auto Task Reviewer Assignment...")

                    # Handle Auto Task reviewer assignment
                    if automation.auto_assign_reviewer:
                        print("✅ Auto-reviewer is enabled!")

                        if task.status == "completed" and not task.auto_assign_reviewer_sent:
                            print(f"🛠 Task '{task.title}' is completed but has not been sent for review. Proceeding...")

                            # 🔹 Fetch workspace admin (who created the group)
                            print("🔍 Fetching group admin profile...")
                            profile = get_object_or_404(Profile, user=group.created_by, organization=organization)
                            print(f"✅ Group Admin: {group.created_by.username}")

                            # 🔹 Fetch Task Details
                            print("🔍 Fetching task details...")
                            time_tracking = TaskTimeTracking.objects.filter(task=task, organization=organization, group=group).first()
                            comments = TaskComment.objects.filter(task=task, organization=organization, group=group)
                            notes = TaskNote.objects.filter(task=task, organization=organization, group=group)
                            attachments = AttachmentsTasksApp.objects.filter(task=task, organization=organization, group=group)
                            subtasks = SubTask.objects.filter(task=task, organization=organization, group=group)
                            activities = ActivityLog.objects.filter(task=task, organization=organization, group=group)

                            print(f"✅ Time Tracking: {time_tracking}")
                            print(f"✅ Found {comments.count()} comments.")
                            print(f"✅ Found {notes.count()} notes.")
                            print(f"✅ Found {attachments.count()} attachments.")
                            print(f"✅ Found {subtasks.count()} subtasks.")
                            print(f"✅ Found {activities.count()} activities.")

                            # 🔹 Render HTML Email
                            print("🔍 Rendering email template...")
                            context = {
                                  "task": task,
                                 "time_tracking": time_tracking,
                                  "comments": comments,
                                     "notes": notes,
                                    "attachments": attachments,
                                     "subtasks": subtasks,
                                    "activities": activities,
                                   "group": group,
                                  "organization": organization,
                                 }
                            email_html_content = render_to_string("task/email/task_review_request.html", context)
                            email_text_content = strip_tags(email_html_content)  # Fallback for clients that don't support HTML

                            # 🔹 Prepare Email
                            print("🔍 Preparing email...")
                            recipient_email = group.created_by.email

                            if not recipient_email:
                                  print("❌ ERROR: No recipient email found! Aborting email send.")
                            else:
                                  print(f"📩 Sending email to: {recipient_email}")

                                  email = EmailMessage(
                                        subject=f"Task Review - {task.title}",
                                        body=email_html_content,
                                        from_email=settings.DEFAULT_FROM_EMAIL,
                                        to=[recipient_email],
                                      )
                                  email.content_subtype = "html"  # Send as HTML email

                                  # 🔹 Attach Images (Convert URLs to attachments)
                                  if attachments.exists():
                                       print(f"🔍 Attaching {attachments.count()} files...")
                                       for attachment in attachments:
                                            if attachment.attachment:
                                               print(f"📎 Attaching file: {attachment.attachment.path}")
                                               email.attach_file(attachment.attachment.path)  # Attach images
                                  else:
                                      print("ℹ️ No attachments found.")

                                      # 🔹 Send Email
                                  try:
                                     print("📨 Sending email now...")
                                     email.send()
                                     print("✅ Email sent successfully!")
                                  except Exception as e:
                                         print(f"❌ ERROR: Failed to send email! Error: {e}")

                                    # 🔹 Mark task as review notification sent
                                  task.auto_assign_reviewer_sent = True
                                  task.save()
                                  print(f"✅ Task '{task.title}' marked as review notification sent.")

                    else:
                        print("❌ Auto-reviewer is disabled. Skipping task review email.")


                    # Process log activity on completion
                    if automation.log_activity_on_completion:
                        if task.status == 'completed' and not task.log_completion_activity:

                            # Log the activity
                            time_tracking = TaskTimeTracking.objects.filter(task=task, organization=organization, group=group).first()
                            comments = TaskComment.objects.filter(task=task, organization=organization, group=group)
                            notes = TaskNote.objects.filter(task=task, organization=organization, group=group)
                            attachments = AttachmentsTasksApp.objects.filter(task=task, organization=organization, group=group)
                            subtasks = SubTask.objects.filter(task=task, organization=organization, group=group)
                            activities = ActivityLog.objects.filter(task=task, organization=organization, group=group)

                            # prepare the log
                            # Process log activity on completion
                            if automation.log_activity_on_completion:
                               if task.status == 'completed' and not task.log_completion_activity:

                                    # Fetch related objects
                                    time_tracking = TaskTimeTracking.objects.filter(task=task, organization=organization, group=group).first()
                                    comments = TaskComment.objects.filter(task=task, organization=organization, group=group)
                                    notes = TaskNote.objects.filter(task=task, organization=organization, group=group)
                                    attachments = AttachmentsTasksApp.objects.filter(task=task, organization=organization, group=group)
                                    subtasks = SubTask.objects.filter(task=task, organization=organization, group=group)
                                    activities = ActivityLog.objects.filter(task=task, organization=organization, group=group)

                                    # Prepare the log data (Convert QuerySets into JSON serializable data)
                                    # Prepare the log data (Convert QuerySets into JSON serializable data)
                                    action_log = {
                                           "status": "completed",
                                           "timestamp": timezone.now().isoformat(),  # Current timestamp
                                           "comments_added": [{"user": c.user.username, "comment": c.comment, "timestamp": c.created_at.isoformat()} for c in comments],
                                          "files_uploaded": [{"user": att.user.username, "file": att.attachment.name, "description": att.description} for att in attachments],
                                          "notes": [{"user": n.user.username, "note": n.note, "timestamp": n.created_at.isoformat()} for n in notes],
                                          "time_spent": float(time_tracking.time_spent) if time_tracking and time_tracking.time_spent else "N/A",  # FIX HERE
                                          "subtasks": [{"title": sub.title, "status": sub.status, "progress": float(sub.progress)} for sub in subtasks],  # FIX HERE
                                          "activities": [{"user": act.user.username, "action": act.action, "details": act.details, "timestamp": act.timestamp.isoformat()} for act in activities],
                                       }

                                    # Log the activity
                                    TaskCompletionActivities.objects.create(
                                          organization=task.organization,
                                          task=task,
                                          group=task.group,
                                          accomplisher=task.assigned_to,
                                          action=action_log,
                                       )


                                    # Send Email to the user about task log
                                    # Prepare Email Content
                                    context = {
                                          "task": task,
                                           "log": {
                                          "time_spent": time_tracking.time_spent if time_tracking else "N/A",
                                            "comments_added": comments,
                                           "files_uploaded": attachments,
                                           "notes": notes,
                                           "subtasks": subtasks,
                                            "activities": activities
                                       },
                                          "organization": organization.name,
                                          "group":group.name,
                                          "project_manager":task.created_by.username, 
                                          "workspace_admin":group.created_by.username
                                       }

                                    email_html_content = render_to_string("task/email/task_log.html", context)
                                    email_text_content = strip_tags(email_html_content) 

                                    # Send Email
                                    email = EmailMessage(
                                            subject=f"Task Log - {task.title}",
                                            body=email_html_content,
                                            from_email=settings.DEFAULT_FROM_EMAIL,
                                             to=[task.assigned_to.email]
                                       )
                                    email.content_subtype = "html"  
                                    email.send()

                                    print(f"✅ Task log email sent to {task.assigned_to.email} for task: {task.title}")

                                    # Mark task as logged
                                    task.log_completion_activity = True
                                    task.save()

                    print(f"✅ Task completion logged for task: {task.title}")

                    # Task chaining notification
                    if automation.assign_task_if_previous_completed:
                        if task.status == 'completed' and not task.task_chaining_notification_sent:

                            # send email to the manager that the user is available for new tasks
                            subject=f'{task.assigned_to.username} Is Open For New Tasks'
                            
                            message = (
                                  f"Dear {task.created_by.username},\n\n"
                                  f"We are pleased to inform you that **{task.assigned_to.username}** has successfully completed the task **\"{task.title}\"** "
                                  f"that was assigned to them. Their commitment and efficiency in handling tasks have been commendable.\n\n"
    
                                  f"🎯 **Task Summary:**\n"
                                  f"- **Title:** {task.title}\n"
                                  f"- **Priority:** {task.priority}\n"
                                  f"- **Completed On:** {timezone.localtime(task.updated_at).strftime('%Y-%m-%d %H:%M')}\n\n"
                                  f'-**Workspace:** {task.organization.name}\n\n'
                                  f"-**Group:** {task.group.name}"
     
                                  f"With this task now completed, **{task.assigned_to.username}** is available to take on new responsibilities. "
                                  f"We encourage you to leverage their skills and assign them new tasks as needed.\n\n"
    
                                   f"💡 **Next Steps:**\n"
                                   f"➡️ Review the completed task if needed.\n"
                                   f"➡️ Assign a new task to {task.assigned_to.username}.\n"
                                   f"➡️ Provide feedback to enhance productivity.\n\n"
    
                                    f"Thank you for your leadership and for keeping projects moving efficiently.\n\n"
    
                                    f"Best Regards,\n"
                                    f"**Team CalendarPlus**"
                               )

                            from_email = settings.DEFAULT_FROM_EMAIL
                            recipient_list=[task.created_by.email]

                            # send the mail
                            send_mail(subject,message,from_email,recipient_list)

                            # send notification to the user 
                            subject_assignee=f'Task Chaining Request Sent'
                            message_assignee = (
                                 f"Dear {task.assigned_to.username},\n\n"
                                 f"First of all, we sincerely appreciate your efforts in completing the task **\"{task.title}\"**. "
                                 f"Your dedication and efficiency are truly valued.\n\n"
    
                                 f"🔗 **Task Chaining Enabled**\n"
                                 f"As per your task settings, **task chaining** has been enabled for you. "
                                 f"We have sent a chaining request to your manager (**{task.created_by.email}**) for further task assignments.\n\n"
    
                                 f"🏢 **Workspace & Group Details:**\n"
                                 f"- **Workspace:** {task.organization.name}\n"
                                 f"- **Group:** {task.group.name}\n\n"
    
                                 f"Thank you for your continued contributions. "
                                 f"We look forward to your participation in upcoming tasks.\n\n"
    
                                 f"Best Regards,\n"
                                 f"**Team CalendarPlus**"
                                  )
                            from_email=settings.DEFAULT_FROM_EMAIL
                            recipient_list_assignee=[task.assigned_to.email]

                            send_mail(subject=subject_assignee,message=message_assignee,from_email=from_email,recipient_list=recipient_list_assignee)


                            # mark the task
                            task.task_chaining_notification_sent = True
                            task.save()

                    self.stdout.write(self.style.SUCCESS(f" Task chaining notification sent for task: {task.title}"))



                    # Install New Task Management app automatically or update 
                    if automation.install_new_apps:
                        if not task.install_new_app_notification:

                            # Get the latest task management app
                            latest_task_app = MiniApp.objects.filter(category="task_management").order_by('-created_at').first()

                            # Limit auto-installation to only 5 apps
                            if MiniApp.objects.filter(category="task_management").count() > 5 or not latest_task_app:
                                 return  

                            organization = task.organization 

                            # Find the first admin of the organization
                            admin_user = task.assigned_to

                            if admin_user:
                                InstalledMiniApp.objects.get_or_create(
                                   user=admin_user,
                                   organization=organization,
                                   mini_app=latest_task_app
                                 )
                               
                                #notify the user about app installation
                                subject=f'New App Installed - {latest_task_app.name}'
                                message=(
                                    f'New App Installed from CalAppsStore\n'
                                    f'Dear {task.assigned_to.username}\n'
                                    f'We have just installed new app in your account\n'
                                    f'As per the settings you enabled to install new task management app if it releases on CalAPPStore\n'
                                    f'App Details are below\n\n'
                                    f'App Name: {latest_task_app.name}\n'
                                    f'Size: {latest_task_app.size}\n'
                                    f'Description: {latest_task_app.description}\n'
                                    f'Category: {latest_task_app.category}\n'
                                    f'Developer:{latest_task_app.developer}\n'
                                    f'Released At: {latest_task_app.created_at}\n'
                                    f'Thank You\n'
                                    f'Team CalAppsStore'

                                )
                                from_email=settings.DEFAULT_FROM_EMAIL
                                recipient_email=[task.assigned_to.email]
                                # send the email   
                                send_mail(subject,message,from_email,recipient_list)
                                  

                                # Mark notification as sent
                                task.install_new_app_notification = True
                                task.save()

                    self.stdout.write(self.style.WARNING(f"⚠️ Task Management apps installed for : {task.title}"))

      

                    # Deadline extention if task is 80% completed 
                    if automation.extend_deadline:
                        if task.progress >= 80 and task.deadline - timezone.now() < timedelta(hours=24) and not task.deadline_extend_notification:
                            task.deadline += timedelta(days=2)   

                            # notify about deadline extinction to manager and user     
                            subject_manager=f'Deadline Extend - {task.title}'
                            message_manager = (
                                f"Dear {task.created_by.username},\n\n"
                                f"We want to inform you that the deadline for the task **'{task.title}'** assigned to **{task.assigned_to.username}** "
                                f"in the group **'{group.name}'** under the organization **'{organization.name}'** has been extended.\n\n"
                                 f"This extension has been applied based on **{task.assigned_to.username}’s task settings** and your organization's policy, "
                                f"since they have successfully completed **{task.progress}%** of the task.\n\n"
                                f"🔹 **New Deadline:** {task.deadline.strftime('%Y-%m-%d %H:%M')}\n\n"
                                f"We encourage you to review the updated timeline and provide any further instructions if needed.\n\n"
                                f"Thank you for using CalendarPlus!\n\n"
                                f"Best Regards,\n"
                                f"**Team CalendarPlus**"
                            )

                            from_email=settings.DEFAULT_FROM_EMAIL
                            recipient_list_manager=[task.created_by.email]

                            # send mail
                            send_mail(subject=subject_manager,message=message_manager,from_email=from_email,recipient_list=recipient_list_manager)

                            # send the email to the user (task.assigned_to)
                            subject_user = f"Task Deadline Extended for {task.title}"
                            message_user = (
                               f"Dear {task.assigned_to.username},\n\n"
                               f"We appreciate your efforts in completing **{task.progress}%** of the task **'{task.title}'** "
                               f"in the group **'{group.name}'** under the organization **'{organization.name}'**.\n\n"
                               f"Based on your progress and according to the company policy, we have **extended your task deadline** to give you additional time to complete the remaining work.\n\n"
                               f"🔹 **New Deadline:** {task.deadline.strftime('%Y-%m-%d %H:%M')}\n\n"
                               f"Please utilize this extended period effectively to ensure the successful completion of your task.\n\n"
                               f"If you need any further assistance, feel free to reach out.\n\n"
                               f"Thank you for your dedication!\n\n"
                               f"Best Regards,\n"
                               f"**Team CalendarPlus**"
                              )
                            
                            recipient_list_user = [task.assigned_to.email]
                            from_email=settings.DEFAULT_FROM_EMAIL
                            send_mail(subject=subject_user, message=message_user, from_email=from_email, recipient_list=recipient_list_user)

                            # mark the notification as sent 
                            task.deadline_extend_notification = True
                            task.save()

                    self.stdout.write(self.style.WARNING(f"⚠️ Task deadline extend notification sent for: {task.title}"))

           

                    # Auto escalate task if no progress made in 48 hours     
                    if automation.automate_stalled:
                           if task.progress == 0 and (timezone.now() - task.updated_at).total_seconds() > 172800 and not task.automate_stalled_action:
                               
                                subject_manager_stalled = f"🚨 Task Escalation Alert: {task.title}"
                                recipient_list_manager_stalled=[task.created_by.email]
                                message_manager_stalled = (
                                    f"Dear {task.created_by.username},\n\n"
                                    f"The task **'{task.title}'** assigned to **{task.assigned_to.username}** in the group **'{group.name}'** under the organization **'{organization.name}'** "
                                    f"has not shown any progress in the last **48 hours**.\n\n"
                                    f"📌 **Task Details:**\n"
                                    f"🔹 **Task Name:** {task.title}\n"
                                    f"🔹 **Assigned To:** {task.assigned_to.username} ({task.assigned_to.email})\n"
                                    f"🔹 **Group:** {group.name}\n"
                                    f"🔹 **Organization:** {organization.name}\n"
                                    f"🔹 **Last Updated:** {task.updated_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                                    f"We recommend checking in with **{task.assigned_to.username}** to understand any challenges and ensure smooth progress.\n\n"
                                    f"Please take the necessary action to prevent delays.\n\n"
                                    f"Best Regards,\n"
                                    f"**Team CalendarPlus**"
                                 )
                                from_email=settings.DEFAULT_FROM_EMAIL

                                # SEND THE EMAIL TO THE MANAGER
                                send_mail(
                                      subject=subject_manager_stalled,
                                      message=message_manager_stalled,
                                      from_email=from_email,
                                      recipient_list=recipient_list_manager_stalled
                                     )
                                
                                # send email to the assignee
                                subject_user_stalled = f"⏳ Task Escalation Alert: {task.title}"
                                message_user_stalled = (
                                     f"Dear {task.assigned_to.username},\n\n"
                                     f"We noticed that there has been **no progress** on your assigned task **'{task.title}'** "
                                     f"in the group **'{group.name}'** under the organization **'{organization.name}'** for the last **48 hours**.\n\n"
                                     f"📌 **Task Details:**\n"
                                     f"🔹 **Task Name:** {task.title}\n"
                                     f"🔹 **Assigned By:** {task.created_by.username} ({task.created_by.email})\n"
                                     f"🔹 **Group:** {group.name}\n"
                                     f"🔹 **Organization:** {organization.name}\n"
                                     f"🔹 **Last Updated:** {task.updated_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                                     f"If you are facing any blockers, please reach out to your manager **{task.created_by.username}** to discuss any required support or assistance.\n\n"
                                     f"Your timely efforts help ensure smooth task management and project success.\n\n"
                                     f"Best Regards,\n"
                                     f"**Team CalendarPlus**"
                                    )
                                recipient_list_user_stalled = [task.assigned_to.email]
                                send_mail(
                                   subject=subject_user_stalled,
                                   message=message_user_stalled,
                                   from_email=settings.DEFAULT_FROM_EMAIL,
                                   recipient_list=recipient_list_user_stalled
                                )
                                # mark the action as happened
                                task.automate_stalled_action = True
                                task.save()


                    self.stdout.write(self.style.WARNING(f"⚠️Automated Stalled task: {task.title}"))


                    # Smart Task Priortization 
                    # 🚀 Smart Task Prioritization: Escalate to URGENT if Not Started & Deadline Near
                    if automation.task_priortization:
                       if task.progress == 0 and not task.task_priortization_update:  # No progress made
                           hours_remaining = (task.deadline - timezone.now()).total_seconds() / 3600  # Convert to hours

                           if hours_remaining <= 12 and not task.task_priortization_update:
                                task.priority = "urgent"  # Force update to urgent
                                task.task_priortization_update=True
                                task.save(update_fields=["priority"])  # Save only required fields

                                # 📩 Email for Task Assignee (task.assigned_to)
                                subject_assignee = f"🚨 Urgent Task Alert: {task.title}"
                                recipient_list_assignee=[task.assigned_to.email]
                                recipient_list_manager=[task.created_by.email]
                                message_assignee = (
                                     f"Dear {task.assigned_to.username},\n\n"
                                     f"The task **'{task.title}'** in **{task.group.name}** under **{task.organization.name}** "
                                     f"is **approaching its deadline** and has **not been started yet**.\n"
                                     f"To ensure timely completion, the system has **escalated its priority to URGENT**.\n\n"
                                      f"🔹 **Deadline:** {task.deadline.strftime('%Y-%m-%d %H:%M')}\n"
                                     f"🔹 **Assigned By:** {task.created_by.username}\n"
                                     f"🔹 **New Priority:** 🚨 URGENT\n\n"
                                     f"Please take immediate action to complete this task on time.\n\n"
                                     f"Best Regards,\n"
                                      f"**Team CalendarPlus**"
                                      )

                                # 📩 Email for Task Manager (task.created_by)
                                subject_manager = f"⚠️ Task Escalation: {task.title} is Now URGENT"
                                message_manager = (
                                        f"Dear {task.created_by.username},\n\n"
                                        f"The task **'{task.title}'** assigned to **{task.assigned_to.username}** "
                                        f"in **{task.group.name}** under **{task.organization.name}** has **not started yet** "
                                        f"and is nearing its deadline.\n"
                                        f"To avoid delay, the system has **automatically escalated its priority to URGENT**.\n\n"
                                        f"🔹 **Deadline:** {task.deadline.strftime('%Y-%m-%d %H:%M')}\n"
                                        f"🔹 **Current Progress:** 0%\n"
                                        f"🔹 **New Priority:** 🚨 URGENT\n\n"
                                        f"📢 Please follow up with {task.assigned_to.username} to ensure timely completion.\n\n"
                                        f"Best Regards,\n"
                                        f"**Team CalendarPlus**"
                                     )

                                # Send emails separately
                                send_mail(
                                   subject=subject_assignee,
                                   message=message_assignee,
                                   from_email=settings.DEFAULT_FROM_EMAIL,
                                   recipient_list=recipient_list_assignee
                                )

                                send_mail(
                                      subject=subject_manager,
                                      message=message_manager,
                                      from_email=settings.DEFAULT_FROM_EMAIL,
                                      recipient_list=recipient_list_manager
                                  )
                               

                                print(f"📧 Urgent Priority Alert Sent for Task: {task.title}")

                    self.stdout.write(self.style.WARNING(f"Urgent priority alert action triggered for : {task.title}"))

            
                    # Auto schedule meeting after task submission for review 
                    
                    # Auto schedule meeting after task submission for review
                    if automation.auto_schedule_meeting_on_approval:
                        print(f"🔍 Checking task '{task.title}' (ID: {task.id}) for auto-scheduling...")

                        if task.status == "pending_approval" and not task.auto_meeting_scheduled:
                            print("✅ ACTION HITTED FOR AUTO SCHEDULE MEETING...")

                            assigned_user = task.created_by
                            task_assignee = task.assigned_to

                            print(f"📝 Task '{task.title}' is pending approval. Finding available slots for {assigned_user.username}...")

                            # Fetch first available slot
                            slot = Availability.objects.filter(
                                user=assigned_user,
                                organization=task.organization,
                                is_booked=False
                            ).order_by("day_of_week", "start_time").first()

                            if not slot:
                                print(f"⚠️ No available slots found for {assigned_user.username}. Cannot auto-schedule a meeting.")
                            else:
                                today = timezone.now().date()
                                days_ahead = (slot.day_of_week - today.weekday()) % 7
                                meeting_date = today + timedelta(days=days_ahead)

                                print(f"📅 Selected Meeting Date: {meeting_date}")
                                print(f"⏳ Using Slot Time: {slot.start_time} - {slot.end_time}")

                                try:
                                    # ✅ Convert to timezone-aware datetime
                                    start_time = timezone.make_aware(datetime.combine(meeting_date, slot.start_time))
                                    end_time = timezone.make_aware(datetime.combine(meeting_date, slot.end_time))
                                except Exception as e:
                                    print(f"⚠️ Time conversion failed: {e}. Using default times.")
                                    # ✅ Fallback to 9 AM - 10 AM if there's any issue
                                    start_time = timezone.make_aware(datetime.combine(meeting_date, time(9, 0)))
                                    end_time = timezone.make_aware(datetime.combine(meeting_date, time(10, 0)))

                                print(f"✅ Scheduling Meeting: {start_time} to {end_time}")

                                # Schedule the meeting
                                meeting = MeetingTaskQuery.objects.create(
                                    organization=task.organization,
                                    group=task.group,
                                    task=task,
                                    scheduled_by=task_assignee,
                                    task_creator=assigned_user,
                                    date=meeting_date,
                                    start_time=start_time,  # ✅ Now a timezone-aware datetime
                                    end_time=end_time,  # ✅ Now a timezone-aware datetime
                                    reason="need_clarification",
                                    meeting_link="https://meet.google.com/new",
                                    status="pending"
                                )

                                # Mark the slot as booked
                                slot.is_booked = True
                                slot.save()

                                print(f"✅ Meeting scheduled successfully for {assigned_user.username} on {meeting_date} at {slot.start_time}.")

                                # Send meeting notifications
                                subject_creator = f"Meeting Scheduled for Task Approval - {task.title}"
                                message_creator = (
                                    f"Dear {assigned_user.username},\n\n"
                                    f"A meeting has been scheduled for {task_assignee.username} to discuss task approval for '{task.title}'.\n"
                                    f"Meeting Details:\n"
                                    f"📅 Date: {meeting_date}\n"
                                    f"⏰ Time: {slot.start_time} - {slot.end_time}\n"
                                    f"📍 Meeting Link: {meeting.meeting_link}\n\n"
                                    f"Best,\nTeam CalendarPlus"
                                )

                                subject_assignee = f"Task Approval Meeting Scheduled - {task.title}"
                                message_assignee = (
                                    f"Dear {task_assignee.username},\n\n"
                                    f"A meeting has been scheduled for you to discuss the approval of the task '{task.title}'.\n"
                                    f"Meeting Details:\n"
                                    f"📅 Date: {meeting_date}\n"
                                    f"⏰ Time: {slot.start_time} - {slot.end_time}\n"
                                    f"📍 Meeting Link: {meeting.meeting_link}\n\n"
                                    f"Please be prepared with any necessary details regarding the task.\n\n"
                                    f"Best,\nTeam CalendarPlus"
                                )

                                try:
                                    send_mail(
                                        subject=subject_creator,
                                        message=message_creator,
                                        from_email=settings.DEFAULT_FROM_EMAIL,
                                        recipient_list=[task.assigned_to.email]
                                    )
                                    print(f"📩 Email sent to {assigned_user.username} ({assigned_user.email}) successfully!")
                                except Exception as e:
                                    print(f"❌ Failed to send email to {assigned_user.username}: {e}")

                                try:
                                    send_mail(
                                        subject=subject_assignee,
                                        message=message_assignee,
                                        from_email=settings.DEFAULT_FROM_EMAIL,
                                        recipient_list=[task.created_by.email]
                                    )
                                    print(f"📩 Email sent to {task_assignee.username} ({task_assignee.email}) successfully!")
                                except Exception as e:
                                    print(f"❌ Failed to send email to {task_assignee.username}: {e}")

                                # Mark task as having an auto-scheduled meeting
                                task.auto_meeting_scheduled = True
                                task.save()

                                print(f"📌 Task '{task.title}' marked as having a scheduled meeting.")

                    # Overdue Notification 
                    if automation.overdue_notification and task.deadline < timezone.now().date() and task.status != "completed" and not task.overdue_notification_sent:
                            print(f"⚠️ Task '{task.title}' is overdue! Updating status...")

                            # Update task status to 'overdue'
                            task.status = "overdue"
                            task.overdue_notification_sent = True
                            task.save()

                            print(f"🔴 Task '{task.title}' status set to OVERDUE.")

                            # Email notifications
                            subject = f"Task Overdue Alert: {task.title}"
                            message = (
                                f"Dear {task.created_by.username} & {task.assigned_to.username},\n\n"
                                f"The task '{task.title}' has exceeded its deadline and is now marked as OVERDUE.\n"
                                f"📅 Deadline: {task.deadline}\n"
                                f"⚠️ Please review and take the necessary actions immediately.\n\n"
                                f"Best,\nTeam CalendarPlus"
                            )

                            recipient_list = [task.created_by.email, task.assigned_to.email]

                            try:
                                send_mail(
                                    subject=subject,
                                    message=message,
                                    from_email=settings.DEFAULT_FROM_EMAIL,
                                    recipient_list=recipient_list
                                )
                                print(f"📩 Overdue email sent successfully to {recipient_list}!")
                            except Exception as e:
                                print(f"❌ Failed to send overdue email: {e}")       

# Automations Ends Here-------------------------------------------------------------------------------------------------- 
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"❌ Error processing automation: {str(e)}"))

        self.stdout.write(self.style.SUCCESS("🎯 All automations processed successfully!"))
