from django.db import models
from accounts.models import Organization, Profile
from django.contrib.postgres.fields import JSONField  
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class BookMarksWidget(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='bookmarkss')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_bookmarks')
    data = models.JSONField(default=list)  # Each item in the list will be a bookmark object
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.organization.name} | {self.created_by.username} | {len(self.data)} bookmarks"