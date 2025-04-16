from django.db import models
from accounts.models import Organization, Profile
from django.contrib.auth.models import User

# Create your models here.

# Store Dashboard Info
class DashboardWidget(models.Model):
    WIDGET_CHOICES = [
        ('calendar', 'Calendar'),
        ('tasks', 'Today\'s Tasks'),
        ('meetings', 'Upcoming Meetings'),
        ('notes', 'Notes'),
        ('leaderboard', 'Leaderboard'),
        ('calculation','Calculation'),
        ('workload','Workload'),
        ('progress','Progress'),
        ('overdue_tasks','Overdue tasks'),
        ('due_soon','Due soon'),
        ('bookmarks','Bookmarks'),
        ('resources','Resources'),
        ('recent_activity','Recent activity'),
        ('channels','Channels'),
        ('time_traced','Time traced'),
        ('high_priority_tasks','High priority tasks'),
        ('calpoints','Calpoints'),
        ('google_docs','Google docs'),
        ('google_sheets','Google sheets'),
        ('youtube','Youtube'),
        ('figma','Figma'),
        ('tasks_in_progress','Tasks in progress'),
        ('completed_tasks','Completed tasks'),
        ('status_over_time','Status over time'),
        ('tag_usage','Tag usage'),
        ('discussion','Discussion'),
        ('total_time_traced','Total time traced'),
        ('tasks_by_assignee','Tasks by assignee'),
        # Add more widgets as you scale, my baby 💖
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='dashboard_widgets')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboard_widgets')
    widget_type = models.CharField(max_length=50, choices=WIDGET_CHOICES)
    position = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('organization', 'user', 'widget_type')  # one widget type per user/org
        ordering = ['position']

    def __str__(self):
        return f"{self.user.username}'s {self.get_widget_type_display()} in {self.organization.name}"
