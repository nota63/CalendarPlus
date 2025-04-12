from django.db import models
from accounts.models import Organization, Profile
from django.contrib.postgres.fields import JSONField  
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now
# Create your models here.

class BookMarksWidget(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='bookmarkss')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_bookmarks')
    data = models.JSONField(default=list)  # Each item in the list will be a bookmark object
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.organization.name} | {self.created_by.username} | {len(self.data)} bookmarks"
    

# widget 3 ) Recent Activities 
class RecentActivity(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ("create", "Created"),
        ("update", "Updated"),
        ("delete", "Deleted"),
        ("read", "Read"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activitiess',null=True, blank=True)

    path = models.CharField(max_length=1024, help_text="Full path accessed (with or without query string).",null=True,blank=True)
    method = models.CharField(max_length=10, help_text="HTTP method used.",null=True, blank=True)

    activity_type = models.CharField(
        max_length=10, choices=ACTIVITY_TYPE_CHOICES, default='other',
        help_text="Type of action performed.",null=True, blank=True
    )
    model_name = models.CharField(
        max_length=255, blank=True, null=True, help_text="Name of the model affected (optional)."
    )
    object_id = models.CharField(
        max_length=255, blank=True, null=True, help_text="ID of the object affected (optional)."
    )

    description = models.TextField(blank=True, null=True, help_text="Optional human-readable context.")

    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    extra_data = models.JSONField(blank=True, null=True, help_text="Optional JSON context for flexibility.")
    timestamp = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Recent Activity"
        verbose_name_plural = "Recent Activities"

    def __str__(self):
        return f"{self.user} {self.activity_type} via {self.method} at {self.path}"
