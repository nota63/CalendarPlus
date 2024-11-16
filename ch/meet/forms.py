from django import forms
from django.contrib.auth.models import User
from .models import Meeting,Docs, Birthday, Reminder


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['title', 'date', 'time', 'user']


# model to update email addresses        
class UpdateEmailForm(forms.ModelForm):
    email=forms.EmailField(label='Enter Your Email To Update', required=True)
    class Meta:
        model= User
        fields=['email']



# docs form

class DocsForm(forms.ModelForm):
    TASK_CHOICES = [
        ('', 'Select Task'),  # Default empty option
        ('important_task', 'Important Task'),  # Option requiring due date
        ('regular_task', 'Regular Task'),
        # Add other options as needed
    ]
    
    task = forms.ChoiceField(choices=TASK_CHOICES)  # Dropdown for task

    class Meta:
        model = Docs
        fields = ['meeting', 'notes', 'documents', 'task', 'due_date','task_title']
        widgets = {
            'task_title': forms.TextInput(attrs={'style': 'display: none;'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'style': 'display: none;'}),
          
        }

class BirthdayForm(forms.ModelForm):
    class Meta:
        model = Birthday
        fields = ['name','phone_number', 'birthdate', 'message', 'scheduled_time']
        widgets = {
            'birthdate': forms.DateInput(attrs={'class': 'flatpickr-date'}),
            'scheduled_time': forms.DateTimeInput(attrs={'class': 'flatpickr-datetime'}),
        }

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        
        fields= ['meeting','reminder_datetime']
        widgets={
            'reminder_datetime':forms.DateTimeInput(attrs={'type':'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        self.request= kwargs.pop('request', None)
        super(ReminderForm, self).__init__(*args, **kwargs)

        if self.request and self.request.user.is_authenticated:
            user = self.request.user
            self.fields['meeting'].queryset=Meeting.objects.filter(user=user)

        self.fields['meeting'].label = 'Select a Meeting'
         

