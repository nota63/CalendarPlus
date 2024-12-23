from django import forms
from .models import HolidayOrganization


class HolidayMessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, label='Message', required=True)


class HolidayForm(forms.ModelForm):
    class Meta:
        model = HolidayOrganization
        fields = ['name', 'description', 'start_date', 'end_date','message_for_invitees']