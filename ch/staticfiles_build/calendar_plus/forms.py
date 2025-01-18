from django import forms
from django.contrib.auth.models import User
from accounts.models import Profile, Organization, EmailInvitation, ProjectManagerAssignment, Project
from accounts.models import Availability
from django.forms import SelectDateWidget
from meet.models import Meets, Reminder
from django.utils import timezone
from .models import Event

class AddMemberForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=[('manager', 'Manager'), ('employee', 'Employee')],
        label="Role",
        required=True
    )

    class Meta:
        model = Profile
        fields = ['role']  

    def __init__(self, *args, **kwargs):
        # Pop organization to filter users
        self.organization = kwargs.pop('organization')
        super().__init__(*args, **kwargs)

        # Filter out users who are already part of the organization
        self.fields['user'] = forms.ModelChoiceField(
            queryset=User.objects.exclude(profiles__organization=self.organization),
            label="Select User",
            empty_label="Select a user",
            required=True
        )

    def clean(self):
        cleaned_data = super().clean()

        # Get the selected user and role
        user = cleaned_data.get("user")
        role = cleaned_data.get("role")

    
        if Profile.objects.filter(user=user, organization=self.organization).exists():
            raise forms.ValidationError("This user is already a member of the organization.")

       

        return cleaned_data


# EMAIL INVITATION FORM 


class EmailInvitationForm(forms.Form):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=EmailInvitation.ROLE_CHOICES, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = EmailInvitation.ROLE_CHOICES
   

# profile edit form

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user', 'organization'] 
        widgets = {
            'is_admin': forms.CheckboxInput(),
            'is_manager': forms.CheckboxInput(),
            'is_employee': forms.CheckboxInput(),
        }

# calendar part        
# meeting form

 


# share calendar

class ShareCalendarForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}))

class ReminderForm(forms.ModelForm):
    reminder_time = forms.DateTimeField(initial=timezone.now, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = Reminder
        fields = ['reminder_time']

# availability form 


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['start_time', 'end_time', ]
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            
        }


# diifreent pages form 

class OrganizationNameForm(forms.Form):
    name = forms.CharField(max_length=255, label="Organization Name", widget=forms.TextInput(attrs={"placeholder": "Enter organization name"}))

class OrganizationDescriptionForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea(attrs={"placeholder": "Describe your organization"}), required=False)

class ProfileInfoForm(forms.Form):
    full_name = forms.CharField(max_length=255, label="Your Full Name", widget=forms.TextInput(attrs={"placeholder": "Enter your full name"}))
    profile_picture = forms.ImageField(label="Profile Picture", required=False)

class CurrentProjectForm(forms.Form):
    current_project = forms.CharField(max_length=200, label="Current Project", required=False, widget=forms.TextInput(attrs={"placeholder": "Enter current project"}))


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date']

    def clean_end_date(self):
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')

        if end_date and start_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be before start date.")

        return end_date
    
    # assign manager to project 

class AssignManagerForm(forms.ModelForm):
    class Meta:
        model = ProjectManagerAssignment
        fields = ['manager']  # Only include the manager field
    
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        if organization:
            # Filter the manager field to only show managers from the selected organization
            self.fields['manager'].queryset = Profile.objects.filter(
                organization=organization, is_manager=True
            )

            
# assign employyee to managers
class AssignEmployeeForm(forms.Form):
    """Form for assigning employees to a manager in a project."""
    manager = forms.ModelChoiceField(queryset=Profile.objects.none(), empty_label="Select Manager")
    employee = forms.ModelChoiceField(queryset=Profile.objects.none(), empty_label="Select Employee")

    def __init__(self, *args, **kwargs):
        available_employees = kwargs.pop('available_employees', Profile.objects.none())
        super().__init__(*args, **kwargs)
        if available_employees:
            self.fields['employee'].queryset = available_employees


# Event Creation Form
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'duration', 'buffer_time', 'is_recurring', 'location']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter event title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter event description', 'rows': 3}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter duration in minutes'}),
            'buffer_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter buffer time in minutes'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'location': forms.Select(attrs={'class': 'form-control'}) 
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].choices = [
            ('Google Meet', 'Google Meet'),
            ('Zoom', 'Zoom'),
            ('Phone Call', 'Phone Call'),
            ('In Person Meeting', 'In Person Meeting')
        ]

class EventTypeForm(forms.Form):
    EVENT_TYPES = Event.EVENT_TYPES
    event_type = forms.ChoiceField(choices=EVENT_TYPES, widget=forms.RadioSelect)


# edit event form 

class EventEditForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'event_type', 'duration', 'buffer_time', 'is_recurring', 'location']





# booking form
import json

class BookingForm(forms.Form):
    slots = forms.CharField(widget=forms.HiddenInput)

    def clean_slots(self):
        slots_data = self.cleaned_data.get('slots', '[]')
        print(f"Raw slots data: {slots_data}")
        try:
            slots = json.loads(slots_data)
            if not isinstance(slots, list):
                raise forms.ValidationError("Invalid slots format.")
            return slots
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid JSON data for slots.")
