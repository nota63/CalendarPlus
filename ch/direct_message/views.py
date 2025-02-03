# views.py
from django.shortcuts import render, get_object_or_404,redirect
from accounts.models import Organization, Profile
from django.contrib.auth.models import User
from django.http import JsonResponse
from accounts.models import Organization, Profile
from django.contrib.auth.decorators import login_required
from .models import Conversation , Message



# Set  Up

def organization_members(request, organization_id):
    # Fetch the organization using the provided org_id
    organization = get_object_or_404(Organization, id=organization_id)
    
    # Fetch profiles related to the organization (excluding the logged-in user)
    profiles = Profile.objects.filter(organization=organization).exclude(user=request.user)

    # Extract the users from the profiles
    members = [profile.user for profile in profiles]

    # Pass the members to the template
    return render(request, 'direct_messages/fetch_members/organization_members.html', {'organization': organization, 'members': members})



@login_required
def start_chat(request, org_id, user_id):
    # Fetch organization and user to start the chat with
    organization = get_object_or_404(Organization, id=org_id)
    user_to_chat = get_object_or_404(User, id=user_id)

    # Ensure both users belong to the same organization
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    other_user_profile = Profile.objects.filter(user=user_to_chat, organization=organization).first()

    if not user_profile or not other_user_profile:
        return JsonResponse({'error': 'Both users must belong to the same organization.'}, status=400)

    # Check if a conversation already exists between the users
    conversation, created = Conversation.objects.get_or_create(
        user_1=request.user,
        user_2=user_to_chat,
        organization=organization
    )

    # If conversation doesn't exist, create it
    if created:
        Message.objects.create(
            sender=request.user,
            receiver=user_to_chat,
            conversation=conversation,
            content="Conversation started.",
        )

    # Redirect to the conversation page (chat room)
    return redirect('chat_room', conversation_id=conversation.id)
# views.py

@login_required
def chat_room(request, conversation_id):
    # Fetch the conversation based on conversation_id
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if the current user is part of the conversation
    if request.user not in [conversation.user_1, conversation.user_2]:
        return redirect('home')  # Or any other page if the user is not part of the conversation

    # Get the other user in the conversation
    other_user = conversation.get_other_user(request.user)

    # Fetch messages for the conversation
    messages = Message.objects.filter(conversation=conversation).order_by('timestamp')

    # Render the chat room template
    return render(request, 'direct_messages/chat/chat_room.html', {
        'conversation': conversation,
        'messages': messages,
        'organization': conversation.organization,
        'other_user': other_user  # Pass the other user to the template
    })
