from django.shortcuts import render, redirect, get_object_or_404
from .forms import RoomForm
from .models import Room, Invitation
from django.views import View
from django.http import JsonResponse
from plyer import notification
from django.contrib.auth.decorators import login_required
# Create your views here.

image_path = 'chat/cal.ico'

# ACCEPT OR REJECT INVITATIONS

@login_required
def invitation_list(request):
    """Display all invitations to the logged in user"""
    invitations = Invitation.objects.filter(user=request.user,accepted=False)
    return render(request,'chat/invitation_list.html',{'invitations':invitations})

@login_required
def accept_invitation(request, invitation_id):
    """Accept the invitation to a room."""
    # Fetch the specific invitation instance for the logged-in user
    invitation = get_object_or_404(Invitation, id=invitation_id, user=request.user)

    # Call the instance method to accept the invitation
    invitation.accept_invitation()  # Use the instance method

    messages.success(request, 'You have successfully joined the room.')
    return redirect('join_chat', room_name=invitation.room.room_name)  # Ensure correct URL and parameter


@login_required
def reject_invitation(request, invitation_id):
    """Reject the invitation."""
    # Fetch the specific invitation instance for the logged-in user
    invitation = get_object_or_404(Invitation, id=invitation_id, user=request.user)

    # Call the instance method to reject the invitation
    invitation.reject_invitation()  # Use the instance method
    messages.success(request,'Invitation has been rejected successfully')

    messages.info(request, 'Invitation has been rejected.')
    return redirect('invitation_list')  # Ensure correct URL


    






class SelectorView(View):
    template_name = 'chat/selector.html'

    def get(self, request):
        return render(request, self.template_name)
    




from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from .models import Room
from .forms import RoomForm
from django.contrib import messages
from django.urls import reverse
from plyer import notification  
from django.core.mail import send_mail
from django.template.loader import render_to_string


image_path = 'chat/cal.ico'
class JoinRoomView(View):
    template_name = 'chat/create_room.html'

    def get(self, request):
        form = RoomForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RoomForm(request.POST)
        if form.is_valid():
            try:
         
                room = form.save()
                room.users.add(request.user)
                notification.notify(
                    title='Calendar +',
                    message='Room Created Successfully!',
                    app_icon=image_path if image_path else None,
                    timeout=5
                )

                return redirect(reverse('join_chat', kwargs={'room_name': room.room_name}))
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        return render(request, self.template_name, {'form': form})
    
# main             
def join_chat(request, room_name):
    return render(request, 'chat/join_chat.html',{'room_name':room_name})
