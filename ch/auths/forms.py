from django import forms
from django.contrib.auth.models import User
from .models import Profile, Organization, Invitation,EmailInvitation, Availability

class AddMemberForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=[('manager', 'Manager'), ('employee', 'Employee')],
        label="Role",
        required=True
    )

    class Meta:
        model = Profile
        fields = ['role']  # Only role will be used, user is selected in the view

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

        # Ensure that the user is not already a member of the organization
        if Profile.objects.filter(user=user, organization=self.organization).exists():
            raise forms.ValidationError("This user is already a member of the organization.")

        # You can add more custom validation here if needed

        return cleaned_data


# invitation form

class InvitationForm(forms.Form):
    invitee = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        label="Select User"
    )
    role = forms.ChoiceField(
        choices=Invitation.ROLE_CHOICES,
        required=True,
        label="Select Role"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Logged-in user
        super().__init__(*args, **kwargs)

        # Fetch organizations where the user is an admin or manager
        organizations = Organization.objects.filter(
            profiles__user=user,
            profiles__is_admin=True
        ) | Organization.objects.filter(
            profiles__user=user,
            profiles__is_manager=True
        )

        # Set the organization field dynamically
        self.fields['organization'] = forms.ModelChoiceField(
            queryset=organizations.distinct(),
            required=True,
            label="Select Organization"
        )

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
        exclude = ['user', 'organization']  # Exclude user and organization fields
        widgets = {
            'is_admin': forms.CheckboxInput(),
            'is_manager': forms.CheckboxInput(),
            'is_employee': forms.CheckboxInput(),
        }

# calendar part        
# meeting form

from django.forms import SelectDateWidget
from .models import Meets, Reminder
from django.utils import timezone
        


# share calendar

class ShareCalendarForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}))

class ReminderForm(forms.ModelForm):
    reminder_time = forms.DateTimeField(initial=timezone.now, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = Reminder
        fields = ['reminder_time']