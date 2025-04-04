from django.db import models
from django.contrib.auth import get_user_model

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