# forms.py
from django import forms
from accounts.models import Profile

# Step 1: Channel Type
class ChannelTypeForm(forms.Form):
    CHANNEL_TYPE_CHOICES = [
        ('BLANK', 'Blank Channel'),
        ('PROJECT_STARTER', 'Project Starter Kit'),
        ('HELP_REQUESTS', 'Help Requests Process'),
        ('TEAM_SUPPORT', 'Team Support'),
        ('FEEDBACK', 'Feedback Intake and Triage'),
        ('ONBOARDING', 'New Hire Onboarding'),
        ('COACHING', '1:1 Coaching'),
        ('SALES_TRACKING', 'Sales Deal Tracking'),
    ]
    channel_type = forms.ChoiceField(choices=CHANNEL_TYPE_CHOICES)

# Step 2: Channel Name
class ChannelNameForm(forms.Form):
    channel_name = forms.CharField(max_length=255)

# Step 3: Visibility and Allowed Members
class ChannelVisibilityForm(forms.Form):
    VISIBILITY_CHOICES = [
        ('PUBLIC', 'Public - Anyone in Organization'),
        ('PRIVATE', 'Private - Specific People Only'),
    ]
    visibility = forms.ChoiceField(choices=VISIBILITY_CHOICES)
    allowed_members = forms.ModelMultipleChoiceField(queryset=Profile.objects.none(), required=False)
