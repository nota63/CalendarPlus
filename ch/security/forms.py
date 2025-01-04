
from django import forms
from .models import ActivityLog

class ActionSelectionForm(forms.Form):
    actions = forms.MultipleChoiceField(
        choices=ActivityLog.ACTION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )
