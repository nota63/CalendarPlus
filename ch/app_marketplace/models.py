from django.db import models

# Create your models here.


# ADMIN MODEL TO ADD APPS 
class MiniApp(models.Model):
    CATEGORY_CHOICES = [
        ("productivity", "Productivity"),
        ("communication", "Communication"),
        ("task_management", "Task Management"),
        ("entertainment", "Entertainment"),
        ("utility", "Utility"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    icon = models.ImageField(upload_to="mini_apps/icons/", blank=True, null=True)  # App icon
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="other")  # App category
    developer = models.CharField(max_length=255, default="Unknown Developer")  # Developer name
    version = models.CharField(max_length=20, default="1.0")  # App version
    size = models.CharField(max_length=20, default="0.0MB")  # App size
    is_active = models.BooleanField(default=True)  # Enable/disable apps
    is_premium = models.BooleanField(default=False)  # If the app requires a premium subscription
    install_count = models.PositiveIntegerField(default=0)  # Number of times installed
    commands = models.JSONField(default=list)  # Store available commands for the app
    requirements=models.CharField(max_length=255,default="Windows 10 + Higher")
   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.version}"

# Images of miniapp
class MiniAppImage(models.Model):
    mini_app = models.ForeignKey(MiniApp, on_delete=models.CASCADE, related_name="related_imagess")
    image = models.ImageField(upload_to="mini_apps/images/")