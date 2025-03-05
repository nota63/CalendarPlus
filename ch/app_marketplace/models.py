from django.db import models
from django.contrib.auth.models import User
from accounts.models import Organization, Profile,MeetingOrganization

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
    ratings=models.IntegerField(default=0, null=True, blank=True)
    docs=models.TextField(null=True, blank=True)

   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.version}"

# Images of miniapp
class MiniAppImage(models.Model):
    mini_app = models.ForeignKey(MiniApp, on_delete=models.CASCADE, related_name="related_imagess")
    image = models.ImageField(upload_to="mini_apps/images/")



# INSTALL MINI-APP
class InstalledMiniApp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="installed_apps")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="installed_apps")
    mini_app = models.ForeignKey(MiniApp, on_delete=models.CASCADE, related_name="installations")
    installed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("user", "mini_app", "organization") 

    def __str__(self):
        return f"{self.user} installed {self.mini_app} in {self.organization}"



# APPS MODELS -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# TASK MANAGER (KANBAN BOARD)

class TaskManager(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="task_manager_tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[("todo", "To Do"), ("in_progress", "In Progress"), ("done", "Done")],
        default="todo"
    )
    priority = models.CharField(
        max_length=10,
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium"
    )
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasksss")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title}"
    

# ----------------------------------------------------------------------------------------------------------------------------
# BookMarks Manager /---------------------------------

class Bookmark(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="bookmarks"
    )
    title = models.CharField(max_length=255)
    url = models.URLField()
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)  # Optional category
    app_logo = models.ImageField(upload_to="bookmark_logos/", blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.organization.name}"


