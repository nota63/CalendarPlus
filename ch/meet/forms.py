from django import forms
from django.contrib.auth.models import User
from .models import Meeting,Docs


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