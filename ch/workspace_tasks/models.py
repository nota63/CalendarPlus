
from django.db import models
from django.contrib.auth.models import User
from accounts.models import Organization


class TaskOrganization(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creator=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="tasksss")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    depends_on = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name="dependent_tasks")

    class Meta:
        ordering = ['-priority', 'due_date']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    def mark_completed(self):
        """Mark task as completed & auto-update dependent tasks"""
        self.status = "completed"
        self.save()
        # Auto-unblock dependent tasks
        for task in self.dependent_tasks.all():
            task.status = "pending"
            task.save()
