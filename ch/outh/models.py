from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class GoogleAuth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="google_auth")
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    scopes = models.JSONField(default=list)  # Store scopes as a list
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Google Auth for {self.user.username}"
