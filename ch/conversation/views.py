from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import (Conversation, Message,ScheduledMessage)
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
from accounts.models import (Organization,Profile,EventOrganization,MeetingOrganization,BookingOrganization)
from django.db.models import Count, Sum, Avg
from django.utils.timezone import localtime
from datetime import timedelta
from django.conf import settings
import os




User = get_user_model()


@login_required
def chat_view(request, user_id,org_id):
    other_user = get_object_or_404(User, id=user_id)
    organization= get_object_or_404(Organization,id=org_id)

    profile = Profile.objects.filter(organization=organization, user=other_user).first()
    if profile and profile.profile_picture:
      url = profile.profile_picture.url
    else:
       url = None  

    print("URL FOUND:",url)

    # Ensure a unique conversation exists between the two users
    conversation, created = Conversation.objects.get_or_create(
        user1=min(request.user, other_user, key=lambda x: x.id),
        user2=max(request.user, other_user, key=lambda x: x.id),
        organization=organization,
    )

    # Fetch messages related to this conversation
    messages = Message.objects.filter(conversation=conversation,organization=organization).order_by("timestamp").only("text", "file", "timestamp", "sender", "is_read","code_snippet")

    messages.filter(~Q(sender=request.user), is_read=False).update(is_read=True)

   
    # FIXED: Ensure the room name is always the same for the same user pair
    room_name = f"chat_{min(request.user.id, other_user.id)}_{max(request.user.id, other_user.id)}"

    return render(request, "conversation/chats/chat_window.html", {
        "other_user": other_user,
        "messages": messages,
        "room_name": room_name,
        'conversation':conversation,
        'organization':organization,
        'profile':profile,
    })



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
        if not conversation_id:  
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
def save_file(request,org_id):
    organization=get_object_or_404(Organization, id=org_id)
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
            file=file_path,
            organization=organization,
        )

        return JsonResponse({"file_url": file_url})
    return JsonResponse({"error": "No file uploaded"}, status=400)


# save code snippet
@csrf_exempt
def save_code_snippet(request,org_id):
    organization=get_object_or_404(Organization,id=org_id)
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
                user2=max(sender, receiver, key=lambda u: u.id),
                organization=organization
            )

            # Save message with code snippet
            message = Message.objects.create(
                conversation=conversation,
                sender=sender,
                text=None, 
                code_snippet=code_snippet,
                organization=organization
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
def edit_message(request, message_id,org_id):
    organization = get_object_or_404(Organization, id=org_id)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_text = data.get("text", "").strip()
            
            if not new_text:
                return JsonResponse({"success": False, "error": "Message cannot be empty!"}, status=400)

            message = get_object_or_404(Message, id=message_id, sender=request.user)
            message.text = new_text
            message.organization=organization
            message.save()

            # 🔥 SEND MESSAGE ID IN RESPONSE
            return JsonResponse({"success": True, "message_id": message.id, "new_text": message.text})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid data!"}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request!"}, status=405)


# SET MESSAGE RECURRANCE
@csrf_exempt
def set_recurrence(request, message_id,org_id):
    organization = get_object_or_404(Organization,id=org_id)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            repeat_type = data.get("repeat", "none")
            custom_datetime = data.get("custom_datetime", None)

            message = get_object_or_404(Message, id=message_id, sender=request.user)
            message.repeat = repeat_type
            message.organization=organization

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
def delete_message(request, message_id,org_id):
    organization = get_object_or_404(Organization, id=org_id)
    message = get_object_or_404(Message, id=message_id, sender=request.user,organization=organization)
    conversation = message.conversation  
    message.delete()
    
    return redirect(reverse_lazy('dm', kwargs={'user_id': message.conversation.user1.id, 'org_id':message.conversation.organization.id}))



# DELETE ALL MESSAGES 
@login_required
def delete_all_messages(request, conversation_id, org_id):
    if request.method == "POST":
        organization = get_object_or_404(Organization, id=org_id)
        conversation = get_object_or_404(Conversation, id=conversation_id, organization=organization)
        user_input = request.POST.get("workspace_name", "").strip()

        if user_input.lower() == organization.name.lower():
            # Delete all messages where the request.user is the sender
            Message.objects.filter(conversation=conversation, sender=request.user,organization=organization).delete()
            return JsonResponse({"success": True, "message": "All your messages have been deleted!"})
        else:
            return JsonResponse({"success": False, "message": "Workspace name does not match!"})

    return JsonResponse({"success": False, "message": "Invalid request!"}, status=400)


# Overview of messages 


def get_file_size(file_field):
    """Returns file size in bytes, or 0 if no file exists."""
    if file_field and file_field.name:
        file_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
        return os.path.getsize(file_path) if os.path.exists(file_path) else 0
    return 0


def get_text_size(text):
    """Approximate text size in bytes."""
    return len(text.encode('utf-8')) if text else 0


def get_conversation_analytics(request, conversation_id, org_id):
    """Fetch analytics data for a conversation."""
    conversation = get_object_or_404(Conversation, id=conversation_id, organization_id=org_id)
    messages = Message.objects.filter(conversation=conversation, organization_id=org_id)


    total_messages = messages.count()

    total_storage = sum(get_file_size(msg.file) + get_text_size(msg.text) for msg in messages)

    # Storage Used by User (Only Sent Messages)
    user_messages = messages.filter(sender=request.user)
    user_storage = sum(get_file_size(msg.file) + get_text_size(msg.text) for msg in user_messages)

    # Total Code Snippets (Fixing Empty & Null Cases)
    total_code_snippets = messages.filter(code_snippet__isnull=False).exclude(code_snippet="").count()

    # Total Files Sent
    total_files = messages.filter(file__isnull=False).exclude(file="").count()

    # Most Active Day
    most_active_day = messages.values('timestamp__date').annotate(
        count=Count('id')).order_by('-count').first()
    most_active_day = most_active_day['timestamp__date'] if most_active_day else "No Data"

    # Average Messages Per Day
    if total_messages > 0:
        first_message = messages.order_by('timestamp').first().timestamp
        days_active = max((localtime() - first_message).days, 1) 
        avg_messages_per_day = round(total_messages / days_active, 2)
    else:
        avg_messages_per_day = 0

    # Unread Messages Count
    unread_messages = messages.filter(is_read=False).count()

    # Return data as JSON
    return JsonResponse({
        "total_messages": total_messages,
        "total_storage": total_storage, 
        "user_storage": user_storage,  
        "total_code_snippets": total_code_snippets,
        "total_files": total_files,
        "most_active_day": most_active_day,
        "avg_messages_per_day": avg_messages_per_day,
        "unread_messages": unread_messages,
    })




# HANDLE REPEAT MESSAGES 
@login_required
@csrf_exempt
def handle_repeat_status(request, conversation_id, org_id):
    """Fetch or toggle the repeat status of messages with repeat enabled via AJAX."""
    if request.method == "GET":
        messages = Message.objects.filter(
            conversation_id=conversation_id, 
            organization_id=org_id,
            sender=request.user
        ).exclude(repeat="none")  

        messages_list = []
        for msg in messages:
            if msg.text:  
                message_content = msg.text  
            elif msg.code_snippet:
                message_content = f"📜 Code Snippet: {msg.code_snippet[:20]}..."  
            else:
                message_content = "📎 File Message"  

            messages_list.append({
                "id": msg.id,
                "repeat": msg.repeat,
                "custom_repeat_datetime": msg.custom_repeat_datetime,
                "content": message_content  
            })

        return JsonResponse({"messages": messages_list}, safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            message_id = data.get("message_id")
            new_repeat = data.get("repeat")

            message = get_object_or_404(Message, id=message_id, conversation_id=conversation_id, organization_id=org_id)

            if message.sender == request.user:
                message.repeat = new_repeat  
                message.save()
                return JsonResponse({"success": True, "new_repeat": message.repeat})
            else:
                return JsonResponse({"success": False, "error": "Permission denied"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})


# FETCH OTHER USERS MEETINGS,EVENTS

@login_required
def fetch_user_meetings_events(request, org_id, other_user_id):
    """Fetch the latest 3 meetings and events involving the other user."""
    
    try:
        organization = get_object_or_404(Organization, id=org_id)
        other_user = get_object_or_404(User, id=other_user_id)

        # Get 'expand' parameter from AJAX request (default: False)
        expand = request.GET.get("expand", "false").lower() == "true"

        # Define the limit (3 for normal, all if expanded)
        limit = None if expand else 3

        # Fetch meetings where other_user is a participant, sender, or invitee
        meetings = MeetingOrganization.objects.filter(
            organization=organization
        ).filter(
            participants=other_user
        ) | MeetingOrganization.objects.filter(
            organization=organization, user=other_user
        ) | MeetingOrganization.objects.filter(
            organization=organization, invitee=other_user
        ).order_by("-meeting_date", "-start_time")[:limit]

        # Fetch events where other_user is a host or invitee
        events = BookingOrganization.objects.filter(
            organization=organization
        ).filter(
            event_host=other_user
        ) | BookingOrganization.objects.filter(
            invitee=other_user
        ).order_by("-start_time")[:limit]

        # Convert meetings to JSON
        meetings_data = [
            {
                "id": meeting.id,
                "title": meeting.meeting_title,
                "description": meeting.meeting_description,
                "date": meeting.meeting_date.strftime("%Y-%m-%d"),
                "start_time": meeting.start_time.strftime("%H:%M"),
                "end_time": meeting.end_time.strftime("%H:%M"),
                "meeting_link": meeting.meeting_link,
                "meeting_type": meeting.get_meeting_type_display(),
            }
            for meeting in meetings
        ]

        # Convert events to JSON
        events_data = [
            {
                "id": event.id,
                "title": event.event.title,
                "description": event.event.description,
                "start_time": event.start_time.strftime("%Y-%m-%d %H:%M"),
                "end_time": event.end_time.strftime("%Y-%m-%d %H:%M"),
                "location": event.event.location,
                "status": event.status,
            }
            for event in events
        ]

        return JsonResponse({"meetings": meetings_data, "events": events_data}, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# handle message schedule 
@csrf_exempt
def manage_scheduled_messages(request, org_id, conversation_id):
    """Handles scheduling, fetching, and deleting scheduled messages via AJAX."""
    
    if request.method == "POST":
        # Schedule a new message
        organization = get_object_or_404(Organization, id=org_id)
        conversation = get_object_or_404(Conversation, id=conversation_id)
        sender = request.user  # Ensure user is logged in
        
        # Use request.POST for non-file data and request.FILES for files
        scheduled_time = request.POST.get("scheduled_time")
        text = request.POST.get("text", "")
        file = request.FILES.get("file")  # Fetch file properly
        code_snippet = request.POST.get("code_snippet", "")
        schedule_type = request.POST.get("schedule_type", "specific_time")
        custom_interval = request.POST.get("custom_interval")

        scheduled_message = ScheduledMessage.objects.create(
            organization=organization,
            conversation=conversation,
            sender=sender,
            text=text,
            file=file,
            code_snippet=code_snippet,
            scheduled_time=scheduled_time,
            schedule_type=schedule_type,
            custom_interval=custom_interval,
        )

        return JsonResponse({"message": "Scheduled successfully!", "id": scheduled_message.id}, status=201)

    elif request.method == "GET":
        # Fetch all scheduled messages for this conversation
        scheduled_messages = ScheduledMessage.objects.filter(
            organization_id=org_id, conversation_id=conversation_id, is_sent=False
        ).values("id", "text", "file", "code_snippet", "scheduled_time", "schedule_type")

        return JsonResponse({"scheduled_messages": list(scheduled_messages)}, status=200)

    elif request.method == "DELETE":
        try:
            data = json.loads(request.body.decode("utf-8"))  # Decode JSON properly
            message_id = data.get("id")
            scheduled_message = get_object_or_404(ScheduledMessage, id=message_id, organization_id=org_id, conversation_id=conversation_id)

            scheduled_message.delete()
            return JsonResponse({"message": "Deleted successfully!"}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)