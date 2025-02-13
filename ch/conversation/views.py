from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Conversation, Message

User = get_user_model()


@login_required
def chat_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    # Ensure a unique conversation exists between the two users
    conversation, created = Conversation.objects.get_or_create(
        user1=min(request.user, other_user, key=lambda x: x.id),
        user2=max(request.user, other_user, key=lambda x: x.id)
    )

    # Fetch messages related to this conversation
    messages = Message.objects.filter(conversation=conversation).order_by("timestamp")

    # FIXED: Ensure the room name is always the same for the same user pair
    room_name = f"chat_{min(request.user.id, other_user.id)}_{max(request.user.id, other_user.id)}"

    return render(request, "conversation/chats/chat_window.html", {
        "other_user": other_user,
        "messages": messages,
        "room_name": room_name
    })