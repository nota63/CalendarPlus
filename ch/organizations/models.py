from django.db import models
from accounts.models import Organization
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.


# HIDE ORGANIZATION

class OrganizationHide(models.Model):
    from_organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="hidden_by"
    )  
    to_organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="hidden_from"
    )  # The organization being hidden  
    hider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="hidden_organizations"
    )  # The admin who hid the organization  
    hidden_from = models.DateTimeField()  # Start date  
    hidden_until = models.DateTimeField()  # End date  
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  
    notify_members=models.BooleanField(default=False, null=True, blank=True)

    def is_active(self):
        """Check if the hide is currently active"""
        return self.hidden_from <= timezone.now() <= self.hidden_until  

    def __str__(self):
        return f"{self.to_organization.name} hidden by {self.from_organization.name} (Hider: {self.hider.username})"


