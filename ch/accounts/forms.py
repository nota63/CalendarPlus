from django import forms
from .models import HolidayOrganization, Agenda
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from tinymce.widgets import TinyMCE

class HolidayMessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, label='Message', required=True)


class HolidayForm(forms.ModelForm):
    class Meta:
        model = HolidayOrganization
        fields = ['name', 'description', 'start_date', 'end_date','message_for_invitees']

# Agenda form 

class AgendaForm(forms.ModelForm):
    agenda_content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    class Meta:
        model = Agenda
        fields = ['agenda_content']  # Only include the agenda content field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)