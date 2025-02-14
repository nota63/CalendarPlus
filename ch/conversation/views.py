from django.shortcuts import render, get_object_or_404, redirect
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
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import datetime
from django.contrib import messages
from django.urls import reverse_lazy
from accounts.models import Organization

User = get_user_model()


@login_required
def chat_view(request, user_id,org_id):
    other_user = get_object_or_404(User, id=user_id)
    organization= get_object_or_404(Organization,id=org_id)

    # Ensure a unique conversation exists between the two users
    conversation, created = Conversation.objects.get_or_create(
        user1=min(request.user, other_user, key=lambda x: x.id),
        user2=max(request.user, other_user, key=lambda x: x.id),
        organization=organization,
    )

    # Fetch messages related to this conversation
    messages = Message.objects.filter(conversation=conversation,organization=organization).order_by("timestamp")

    # FIXED: Ensure the room name is always the same for the same user pair
    room_name = f"chat_{min(request.user.id, other_user.id)}_{max(request.user.id, other_user.id)}"

    return render(request, "conversation/chats/chat_window.html", {
        "other_user": other_user,
        "messages": messages,
        "room_name": room_name,
        'conversation':conversation,
        'organization':organization,
    })



# SAVE MESSAGES VIA AJAX
# SAVE MESSAGES VIA AJAX
@csrf_exempt
def save_message(request,org_id):

    organization = get_object_or_404(Organization, id=org_id)
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
            text=message_text,
            organization=organization,
           
        )
        return JsonResponse({"status": "success", "message_id": message.id})
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


# SAVE FILES 
@csrf_exempt
def save_file(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        file_path = default_storage.save(f"chat_files/{uploaded_file.name}", uploaded_file)
        file_url = default_storage.url(file_path)

        sender_id = request.POST.get("sender_id")
        conversation_id = request.POST.get("conversation_id")

        # Save file message in DB
        Message.objects.create(
            conversation_id=conversation_id,
            sender_id=sender_id,
            file=file_path
        )

        return JsonResponse({"file_url": file_url})
    return JsonResponse({"error": "No file uploaded"}, status=400)


# save code snippet
@csrf_exempt
def save_code_snippet(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            sender_id = data.get("sender_id")
            receiver_id = data.get("receiver_id")
            code_snippet = data.get("code_snippet", "").strip()

            if not sender_id or not receiver_id or not code_snippet:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            sender = User.objects.get(id=sender_id)
            receiver = User.objects.get(id=receiver_id)

            # Get or create conversation
            conversation, _ = Conversation.objects.get_or_create(
                user1=min(sender, receiver, key=lambda u: u.id),
                user2=max(sender, receiver, key=lambda u: u.id)
            )

            # Save message with code snippet
            message = Message.objects.create(
                conversation=conversation,
                sender=sender,
                text=None,  # No regular text, just the code snippet
                code_snippet=code_snippet
            )

            return JsonResponse({
                "success": True,
                "message_id": message.id,
                "code_snippet": message.code_snippet,
                "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            })

        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid sender or receiver ID"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)



# edit message
@csrf_exempt  
def edit_message(request, message_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_text = data.get("text", "").strip()
            
            if not new_text:
                return JsonResponse({"success": False, "error": "Message cannot be empty!"}, status=400)

            message = get_object_or_404(Message, id=message_id, sender=request.user)
            message.text = new_text
            message.save()

            # 🔥 SEND MESSAGE ID IN RESPONSE
            return JsonResponse({"success": True, "message_id": message.id, "new_text": message.text})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid data!"}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request!"}, status=405)


# SET MESSAGE RECURRANCE
@csrf_exempt
def set_recurrence(request, message_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            repeat_type = data.get("repeat", "none")
            custom_datetime = data.get("custom_datetime", None)

            message = get_object_or_404(Message, id=message_id, sender=request.user)
            message.repeat = repeat_type

            # Handle custom date-time
            if repeat_type == "custom" and custom_datetime:
                try:
                    message.custom_repeat_datetime = datetime.strptime(custom_datetime, "%Y-%m-%dT%H:%M")
                except ValueError:
                    return JsonResponse({"success": False, "error": "Invalid date format!"}, status=400)
            else:
                message.custom_repeat_datetime = None

            message.save()
            return JsonResponse({"success": True, "repeat": message.repeat})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid data!"}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request!"}, status=405)


# Wipe message 
@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    conversation = message.conversation  
    message.delete()
    
    return redirect(reverse_lazy('dm', kwargs={'user_id': message.conversation.user1.id}))

