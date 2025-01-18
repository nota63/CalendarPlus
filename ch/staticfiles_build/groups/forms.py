
from django import forms
from .models import Group, GroupMember


class GroupNameForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        label="Group Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter group name'})
    )

class GroupDescriptionForm(forms.Form):
    description = forms.CharField(
        label="Group Description",
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter group description'}),
        required=False
    )

class TeamLeaderForm(forms.Form):
    email = forms.EmailField(
        label="Team Leader Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address of team leader'})
    )









