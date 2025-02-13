from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Conversation, Message
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import json


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
        "room_name": room_name,
        'conversation':conversation,
    })



# SAVE MESSAGES VIA AJAX
@csrf_exempt
def save_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print("Received Data:", data)  
        message_text = data.get("message")
        sender_id = data.get("sender_id")
        conversation_id = data.get("conversation_id")

        if not conversation_id:  # If conversation_id is empty, return an error
            return JsonResponse({"status": "error", "message": "Conversation ID is missing!"}, status=400)

        sender = User.objects.get(id=sender_id)
        conversation = Conversation.objects.get(id=conversation_id)

        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            text=message_text
        )

        return JsonResponse({"status": "success", "message_id": message.id})

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)