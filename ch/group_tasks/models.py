from django.db import models
from groups.models import Group, GroupMember, GroupEvent, GroupInvitation, GroupEventBooking
from accounts.models import Profile , Organization
from django.contrib.auth.models import User

# Create your models here.



# Model for tasks

class Task(models.Model):
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="The organization under which this task is created."
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="The group this task belongs to."
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        help_text="The user who created this task (e.g., the team leader)."
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        help_text="The group member to whom this task is assigned."
    )

 
    title = models.CharField(
        max_length=255,
        help_text="A short and descriptive title for the task."
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the task."
    )
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent')
        ],
        default='medium',
        help_text="The priority level of the task."
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('overdue', 'Overdue')
        ],
        default='pending',
        help_text="The current status of the task."
    )
    deadline = models.DateTimeField(
        help_text="The deadline for completing the task."
    )
    start_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="The date and time when the task should start."
    )
    end_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="The expected or actual completion date of the task."
    )


    progress = models.PositiveIntegerField(
        default=0,
        help_text="Progress percentage (0-100) of task completion."
    )
    is_recurring = models.BooleanField(
        default=False,
        help_text="Indicates if this task recurs on a schedule."
    )
    recurrence_pattern = models.CharField(
        max_length=50,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly')
        ],
        blank=True,
        null=True,
        help_text="Pattern for recurring tasks."
    )
    recurrence_end_date = models.DateField(
        blank=True,
        null=True,
        help_text="End date for the recurrence pattern."
    )

  
    attachments = models.FileField(
        upload_to='task_attachments/',
        blank=True,
        null=True,
        help_text="Optional file attachments for the task."
    )
    notify_assignee = models.BooleanField(
        default=True,
        help_text="Notify the assignee when the task is created or updated."
    )
    is_urgent_notification_sent = models.BooleanField(
        default=False,
        help_text="Tracks if an urgent notification has been sent for this task."
    )

  
    created_at = models.DateTimeField(auto_now_add=True, help_text="Task creation timestamp.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Task last updated timestamp.")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        constraints = [
            models.CheckConstraint(
                check=models.Q(progress__gte=0) & models.Q(progress__lte=100),
                name='valid_progress_range'
            )
        ]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


    def mark_as_completed(self):
        self.status = 'completed'
        self.progress = 100
        self.save()

    def mark_as_in_progress(self):
        self.status = 'in_progress'
        self.save()

    def cancel_task(self):
        self.status = 'cancelled'
        self.save()

    def is_overdue(self):
        from django.utils.timezone import now
        return self.deadline < now() and self.status not in ['completed', 'cancelled']

    def send_notification(self):
    
        pass





