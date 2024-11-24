from django import forms
from .models import Profile, Organization

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'email', 'contact', 'role','user']

    def __init__(self, *args, **kwargs):
        # pass the current request.user
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            if user.profile.is_manager():
                # managers can add employees only
                self.fields['role'].choices = [
                    ('employee', 'Employee') 
                ]
            elif user.profile.is_profile_admin():
                self.fields['role'].choices = [
                    ('manager', 'Manager'),
                    ('employee', 'Employee')
                ]


class OrganizationForm(forms.ModelForm):
    profile = forms.ModelChoiceField(
        queryset=Profile.objects.all(),
        label="Select User Profile",
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    role = forms.ChoiceField(
        choices=[('manager', 'Manager'), ('employee', 'Employee')],
        label="Assign Role",
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Organization
        fields = ['organization_name', 'profile', 'role']

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        profile = cleaned_data.get('profile')
        # work on current organization instance
        organization = self.instance  

        # Check constraints
        if role == 'manager' and organization.manager:
            raise forms.ValidationError('This organization already has a manager!')

        if role == 'manager' and profile.role != 'manager':
            raise forms.ValidationError('Selected profile is not a manager.')

        if role == 'employee' and profile.role != 'employee':
            raise forms.ValidationError('Selected profile is not an employee.')

        return cleaned_data
    
# form to add employees into the organization
class AddUserToOrganizationForm(forms.ModelForm):
    role_choices = (
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    )

    user = forms.ModelChoiceField(
        queryset=Profile.objects.exclude(role='admin'), 
        label="Select User"
    )
    role = forms.ChoiceField(choices=role_choices, label="Role")

    class Meta:
        model = Organization
        # We will handle user assignment (admin/manager/employee) dynamically.
        fields = []  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude admin profiles from the user list
        self.fields['user'].queryset = Profile.objects.exclude(role='admin')
        