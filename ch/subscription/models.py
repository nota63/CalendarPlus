from django.db import models
from django.contrib.auth import get_user_model
import uuid
from accounts.models import Organization
from django.utils.timezone import now

# get user model
User = get_user_model()


# payment
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.IntegerField()
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount / 100}"


# Premium Plan
class PremiumPlan(models.Model):
    PLAN_CHOICES = [
        ('starter', 'Starter'),
        ('business+', 'Business +'),
        ('enterprise_grid', 'Enterprise Grid'),
    ]

    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)  # ₹ or $
    duration_days = models.PositiveIntegerField(help_text="Plan validity in days")
    description = models.TextField(help_text="Short feature summary or highlights")
    features=models.TextField(help_text="List of features included in the plan", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_name_display()} - ₹{self.price}"

    class Meta:
        ordering = ['price']


# Help Request Model 
class HelpRequest(models.Model):
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='help_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='help_requests')
    title = models.CharField(max_length=255)
    description = models.TextField()
    attachment = models.FileField(upload_to='help_attachments/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.organization.name})"


# Impersonation Summary Model 
class ImpersonationActivityLog(models.Model):
    admin = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    help_request = models.ForeignKey(HelpRequest, on_delete=models.CASCADE,null=True, blank=True)
    path = models.CharField(max_length=512,null=True, blank=True)
    method = models.CharField(max_length=10,null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    request_data = models.JSONField(blank=True, null=True)  # stores GET/POST
    user_agent = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.admin} - {self.path} @ {self.timestamp}"