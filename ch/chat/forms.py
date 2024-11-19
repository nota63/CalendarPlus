from django import forms
from .models import Room, Invitation
from django.contrib.auth.models import User


class RoomForm(forms.ModelForm):
    users_to_invite = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Invite Users'
    )

    class Meta:
        model = Room
        fields = ['room_name']

    def save(self, commit=True):
        # Save the Room object first
        room = super().save(commit=commit)
        
        # After the room is saved, invite the selected users
        if commit:
            users_to_invite = self.cleaned_data.get('users_to_invite', [])
            for user in users_to_invite:
                Invitation.objects.create(room=room, user=user)

        return room