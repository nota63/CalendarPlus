from django.db import models
from groups.models import Group, GroupMember, GroupEvent, GroupInvitation, GroupEventBooking
from accounts.models import Profile , Organization
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now
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



# Add day to track the task
class AddDay(models.Model):
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    timer_start_time = models.DateTimeField(null=True, blank=True)
    timer_end_time = models.DateTimeField(null=True, blank=True)
    timer_running = models.BooleanField(default=False)
    comment = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
   
    TAG_CHOICES = [
        ('urgent', 'Urgent'),
        ('important', 'Important'),
        ('low', 'Low'),
    ]
    tags = models.CharField(max_length=10, choices=TAG_CHOICES, null=True, blank=True)

    # Date added to "My Day" list
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Task {self.task.title} - My Day ({self.user.username})"



# Store task comments , notes , and tags

class TaskComment(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True ) 
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True  ) 
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.title}"

    class Meta:
        ordering = ['created_at']


# Model to store tags for tasks
class TaskTag(models.Model):
    PREDEFINED_TAGS = [
        ('Important', 'Important'),
        ('Urgent', 'Urgent'),
        ('Low Priority', 'Low Priority'),
        ('Completed', 'Completed'),
    ]

    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE,
        related_name='tags'
    )
    name = models.CharField(
        max_length=50,
        choices=PREDEFINED_TAGS,  
    )
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    group = models.ForeignKey(
        Group,  
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        unique_together = ('task', 'name') 


# Model to store notes on tasks
class TaskNote(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)  
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True) 
    note = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Note by {self.user.username} on {self.task.title}"

    class Meta:
        ordering = ['created_at']


# Task timer 

class TaskTimer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)  
    start_time = models.DateTimeField(auto_now_add=True)  
    accumulated_time = models.DurationField(default=timedelta)  
    is_running = models.BooleanField(default=False)

    def __str__(self):
        return f"Timer for {self.task.title} by {self.user.username}"

    def stop_timer(self):
        """Stop the timer and update the accumulated time"""
        if self.is_running:
            self.accumulated_time += (timezone.now() - self.start_time)
            self.is_running = False
            self.save() 


# Show activity log
class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('COMMENT', 'Commented on the task'),
        ('NOTE', 'Added a note'),
        ('START_TIMER', 'Started the timer'),
        ('STOP_TIMER', 'Stopped the timer'),
        ('PROGRESS_UPDATE', 'Updated progress'),
        ('TASK_CREATED', 'Created a task'),
        ('TASK_COMPLETED', 'Marked task as completed'),
        ('TASK_PENDING','Marked task as pending'),
        ('TAG_ADDED','Added a tag in task'),
        ('TAG_REMOVED','Removed the tag from task'),
        ('TIME_SPENT','Spent time on task'),
        ('RAISED_PROBLEM','Raised a problem'),
        ('RESOLVED_PROBLEM','Resolved a problem'),
        ('NOTE_ELIMINATED', 'Eliminated a note'),
        ('NOTE_AMENDED', 'Amended a note'),
        ('COMMENT_MODIFIED','The comment was modified by.'),
        ('COMMENT_DELETED', 'The comment deletion was performed by'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activity_logss")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="activity_logss")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="activity_logss", null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="activity_logss", null=True, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.TextField(null=True, blank=True, help_text="Optional details about the action.")
    timestamp = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"

    def __str__(self):
        return f"{self.user.username} {self.get_action_display()} at {self.timestamp}"


# New Model to track time

class TaskTimeTracking(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="time_tracking")
    organization=models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='time_tracked')
    group=models.ForeignKey(Group, on_delete=models.CASCADE, related_name='time_tracks')
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    time_spent = models.DecimalField(max_digits=5, decimal_places=2) 
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Time tracking for {self.task.title} by {self.user.username}"

    def get_duration(self):
        if self.end_time:
            duration = self.end_time - self.start_time
            return duration.total_seconds() / 3600 
        return 0


# Problem Model

class Problem(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="problems")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="problems")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="problems")
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reported_problems")
    task_created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="problems_created")
    description = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('task', 'reported_by', 'description')
        ordering = ['-created_at']

    def __str__(self):
        return f"Problem in Task: {self.task.title} by {self.reported_by.username}"


