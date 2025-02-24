from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import (Conversation, Message,ScheduledMessage,MessageSuggestion,Todo,Reminder)
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
from django.utils import timezone
from django.utils.timesince import timesince




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
    if profile:
    # Get the last_login of the user
      last_activity = profile.last_login

      if last_activity:
        # Calculate the time difference and format it
        time_diff = timesince(last_activity)

        # If the time difference starts with '0 seconds', we can display "Just now"
        if time_diff.startswith('0 seconds'):
            formatted_time_activity = "Just now"
        else:
            formatted_time_activity = f"{time_diff} ago"
      else:
         formatted_time_activity = "Never logged in"
    else:
        formatted_time_activity = "Profile not found"



    # Ensure a unique conversation exists between the two users
    conversation, created = Conversation.objects.get_or_create(
        user1=min(request.user, other_user, key=lambda x: x.id),
        user2=max(request.user, other_user, key=lambda x: x.id),
        organization=organization,
    )

    # Update last active field
    # Update the last active time for the current user
    user_profile = Profile.objects.get(user=request.user, organization=organization)
    user_profile.last_login = timezone.now()
    user_profile.save()

    conversation.save()

    # Fetch messages related to this conversation
    messages = Message.objects.filter(conversation=conversation,organization=organization).order_by("timestamp").only("text", "file", "timestamp", "sender", "is_read","code_snippet")

    messages.filter(~Q(sender=request.user), is_read=False).update(is_read=True)

   
    # FIXED: Ensure the room name is always the same for the same user pair
    room_name = f"chat_{min(request.user.id, other_user.id)}_{max(request.user.id, other_user.id)}"


    # Fetch users connections
    user=request.user
    # Get all conversations where the user is involved
    conversations = Conversation.objects.filter(Q(user1=user) | Q(user2=user),organization=organization)

    

    chat_users = []
    for convo in conversations:
        second_user = convo.user1 if convo.user2 == user else convo.user2

        profile_2 = Profile.objects.filter(organization=organization, user=second_user).first()
        if profile_2 and profile.profile_picture:
          url = profile.profile_picture.url
        else:
          url = None  

        last_login=profile_2.last_login   
        if last_login:
        # Get the time difference
          time_diff = timesince(last_login)
        # Handle "Just now"
          if time_diff.startswith('Online'):
            formatted_time = "Just now"
          else:
            formatted_time = f"{time_diff} ago"
        else:
           formatted_time = "Never logged in"

        # Count unread messages for this conversation
        unread_count = Message.objects.filter(conversation=convo, is_read=False,organization=organization).exclude(sender=user).count()
        chat_users.append({
            "user": second_user,
            "unread_count": unread_count,
            'profile_2':profile_2,
            'last_login':last_login,
            'formatted_time':formatted_time
        })

    return render(request, "conversation/chats/chat_window.html", {
        "other_user": other_user,
        "messages": messages,
        "room_name": room_name,
        'conversation':conversation,
        'organization':organization,
        'profile':profile,
        'chat_users':chat_users,
        'last_login_profile':formatted_time_activity, 
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



# GET MESSAGES SUGGESTIONS

# def get_message_suggestions(request, org_id):
#     if request.method == 'GET':
#         query = request.GET.get('query', '').strip()

#         # Ensure the organization exists
#         organization = get_object_or_404(Organization, id=org_id)

 
#         suggestions = MessageSuggestion.objects.filter(
#             content__icontains=query, 
#             organization=organization
#         ).values_list('content', flat=True)

#         return JsonResponse({'suggestions': list(suggestions)})


def get_message_suggestions(request, org_id):
    if request.method == 'GET':
        query = request.GET.get('query', '').strip().lower()  # Normalize query

        # Ensure the organization exists
        organization = get_object_or_404(Organization, id=org_id)

        # Fetch suggestions with case-insensitive filtering and flexible matching
        suggestions = MessageSuggestion.objects.filter(
            Q(content__icontains=query) | Q(content__iexact=query),
            organization=organization
        ).only('content').values_list('content', flat=True).distinct()[:50]  # Limit results for efficiency

        # Handle empty results gracefully
        if not suggestions:
            return JsonResponse({'suggestions': [], 'message': "No suggestions found"}, status=200)

        return JsonResponse({'suggestions': list(suggestions)}, status=200)



# CUSTOM COMMANDS / 

# /PROFILE
@login_required
def profile_view(request, org_id):
    try:
        profile = Profile.objects.get(organization_id=org_id, user=request.user)
        org = Organization.objects.get(id=org_id)
        
        # Build the response data
        profile_data = {
            'full_name': profile.full_name if profile.full_name else request.user.username ,
            'role': 'Admin' if profile.is_admin else 'Manager' if profile.is_manager else 'Employee',
            'organization': org.name,
            'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
            'last_login': profile.last_login.strftime('%Y-%m-%d %H:%M:%S') if profile.last_login else 'N/A'
        }
      

        return JsonResponse(profile_data)

    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    

# /WHOIS
from django.utils.timezone import now

@csrf_exempt
@login_required
def whois_view(request, org_id, other_user_id, conversation_id):
    if request.method != "GET":
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    user = request.user  # The logged-in user
    other_user = get_object_or_404(Profile, user_id=other_user_id, organization_id=org_id)
    
    # Count total meetings where either user or other_user is a participant
    total_meetings = MeetingOrganization.objects.filter(
        organization_id=org_id,
        participants__in=[user, other_user.user]
    ).distinct().count()
    
    # Get the latest 2 upcoming meetings
    upcoming_meetings = MeetingOrganization.objects.filter(
        organization_id=org_id,
        participants__in=[user, other_user.user],
        meeting_date__gte=now().date()
    ).order_by('meeting_date', 'start_time')[:2]
    
    # Serialize meeting data
    meetings_data = [
        {
            'meeting_title': meeting.meeting_title,
            'meeting_date': meeting.meeting_date.strftime('%Y-%m-%d'),
            'start_time': meeting.start_time.strftime('%H:%M'),
            'end_time': meeting.end_time.strftime('%H:%M'),
            'meeting_location': meeting.meeting_location,
            'meeting_type': meeting.meeting_type,
        }
        for meeting in upcoming_meetings
    ]
    
    response_data = {
        'full_name': other_user.full_name,
        'role': 'Admin' if other_user.is_admin else 'Manager' if other_user.is_manager else 'Employee',
        'organization': other_user.organization.name if other_user.organization else 'N/A',
        'profile_picture': other_user.profile_picture.url if other_user.profile_picture else '',
        'total_meetings': total_meetings,
        'upcoming_meetings': meetings_data,
    }
    
    return JsonResponse(response_data)


# /RECENT 
# Set up logger for debugging
import logging
logger = logging.getLogger(__name__)

@login_required
def recent_messages(request, org_id, other_user_id, conversation_id, type):
    """Fetches recent messages based on the type (code, message, file)."""
    
    # Ensure the user has access to the conversation
    conversation = get_object_or_404(Conversation, id=conversation_id, organization_id=org_id)
    other_user = get_object_or_404(User, id=other_user_id)
    
    logger.debug(f"Fetching recent {type} messages for conversation {conversation_id} between user {request.user.id} and {other_user.id}")

    # Initialize an empty list for recent data
    recent_data = []

    # Filter the messages based on type
    if type == "code":
        # Get last 5 code snippets sent by the other user
        messages = Message.objects.filter(
            conversation=conversation, sender=other_user, code_snippet__isnull=False
        ).order_by('-timestamp')[:5]
        
        logger.debug(f"Found {len(messages)} code snippets for user {other_user.id}")
        
        recent_data = [{
            'code_snippet': msg.code_snippet,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        } for msg in messages]

    elif type == "message":
        # Get last 5 text messages sent by the other user
        messages = Message.objects.filter(
            conversation=conversation, sender=other_user, text__isnull=False
        ).order_by('-timestamp')[:5]
        
        logger.debug(f"Found {len(messages)} text messages for user {other_user.id}")
        
        recent_data = [{
            'text': msg.text,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        } for msg in messages]

    elif type == "files":
        # Get last 5 files sent by the other user
        messages = Message.objects.filter(
            conversation=conversation, sender=other_user, file__isnull=False
        ).order_by('-timestamp')[:5]
        
        logger.debug(f"Found {len(messages)} files for user {other_user.id}")

        for msg in messages:
            if msg.file:  # Ensure the file exists
                recent_data.append({
                    'file_url': msg.file.url,
                    'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                })
            else:
                logger.debug(f"Message {msg.id} does not have a file associated with it.")
        
        if not recent_data:  # If no files found, send a placeholder message
            recent_data = [{'message': 'No files available.'}]
            logger.debug("No files available for this user.")

    else:
        return JsonResponse({'error': 'Invalid type'}, status=400)

    # Log the final recent data being returned
    logger.debug(f"Returning {len(recent_data)} recent data items for type {type}")

    # Return the recent data as a JSON response
    return JsonResponse({'recent_data': recent_data})


# /JOKES
import pyjokes
import random

def jokes(request):
    # Define joke categories (use only valid ones)
    joke_categories = ['neutral', 'chuck_norris', 'all']  

    # Store jokes from each category
    all_jokes = []
    for category in joke_categories:
        try:
            jokes = pyjokes.get_jokes(language='en', category=category)
            for joke in jokes:
                # Check if joke is a string or an object with .joke
                if isinstance(joke, str):
                    all_jokes.append({
                        'category': category,
                        'joke': joke,  
                        'type': 'single'  
                    })
                else:
                    all_jokes.append({
                        'category': category,
                        'joke': joke.joke,  
                        'type': joke.type  
                    })
        except pyjokes.exc.CategoryNotFoundError:
            print(f"Category '{category}' not found. Skipping.")

    random.shuffle(all_jokes)
    

    all_jokes = all_jokes[:5] 


    return JsonResponse({'jokes': all_jokes})


# Tenor gifs
import requests
def fetch_gifs(request):
    query = request.GET.get('query', '')
    if not query:
        return JsonResponse({'error': 'No query provided'}, status=400)
    
    apikey = "LIVDSRZULELA"  # Your Tenor API key
    limit = 8  # Number of GIFs to fetch
    search_term = query  # Use the query provided by the user
    
    # Fetch the top GIFs using Tenor API
    url = f"https://g.tenor.com/v1/search?q={search_term}&key={apikey}&limit={limit}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        gifs = response.json().get('results', [])
        
        if gifs:
            return JsonResponse({'gifs': gifs})
        else:
            return JsonResponse({'error': 'No GIFs found for the given search term.'}, status=404)
    
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)
    

# /SCHEDULE MESSAGE VIA COMMAND
@csrf_exempt
def schedule_message_command(request, org_id, conversation_id):
    if request.method == 'POST':
        try:
            # Fetch the conversation object using the passed conversation_id
            conversation = get_object_or_404(Conversation, id=conversation_id, organization_id=org_id)
            user = request.user  # Assuming the user is logged in

            # Get data from POST request
            message = request.POST.get('message')
            schedule_time = request.POST.get('schedule_time')  # Format: 'YYYY-MM-DD HH:MM:SS'
            schedule_type = request.POST.get('schedule_type', 'specific_time')  # Default to 'specific_time'

            # Ensure that both schedule_time and message are provided
            if not schedule_time or not message:
                return JsonResponse({'status': 'error', 'message': 'Both time and message are required.'}, status=400)

            # Parse the scheduled time
            try:
                scheduled_time = datetime.strptime(schedule_time, "%Y-%m-%d %H:%M:%S")
                scheduled_time = timezone.make_aware(scheduled_time, timezone.get_current_timezone())
            except ValueError:
                return JsonResponse({'status': 'error', 'message': 'Invalid time format. Please use YYYY-MM-DD HH:MM:SS.'}, status=400)

            # Create ScheduledMessage entry
            scheduled_message = ScheduledMessage.objects.create(
                organization=conversation.organization,
                conversation=conversation,
                sender=user,
                text=message,
                schedule_type=schedule_type,
                scheduled_time=scheduled_time,
            )

            return JsonResponse({'status': 'success', 'message': 'Message scheduled successfully!'})
        
        except Conversation.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Conversation not found.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)



# /todo <due_date> <task> command
@csrf_exempt
def schedule_todo_command(request, org_id, conversation_id):
    if request.method == "POST":
        try:
            print("📥 Raw POST Data:", request.POST)
            conversation = get_object_or_404(Conversation, id=conversation_id, organization_id=org_id)
            user = request.user  

            due_date_str = request.POST.get("due_date")  # Expected format: YYYY-MM-DD HH:MM:SS
            todo_text_raw = request.POST.get("todo")  # Comes with time and actual task
            print(f"🔍 Received - Due Date: {due_date_str}, Raw Todo: {todo_text_raw}")

            if not due_date_str or not todo_text_raw:
                return JsonResponse({"status": "error", "message": "Due date and task are required."}, status=400)

            # Split the input to separate due date and task description
            parts = due_date_str.split(" ", 1)  # Split into date and time part
            if len(parts) < 2:
                return JsonResponse({"status": "error", "message": "Invalid due date format. Expected YYYY-MM-DD HH:MM:SS."}, status=400)
            
            due_date = f"{parts[0]} {parts[1]}"  # Format like '2025-02-19 14:30:00'

            # Extract the todo text (task description)
            todo_text = todo_text_raw.strip()  # Get the actual task text
            print(f"🛠 Merged Date-Time: {due_date}, Task: {todo_text}")

            # Convert to timezone-aware datetime
            try:
                due_date_obj = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
                due_date_obj = timezone.make_aware(due_date_obj, timezone.get_current_timezone())
            except ValueError:
                print("❌ Invalid Date Format:", due_date)
                return JsonResponse({"status": "error", "message": "Invalid date format. Use YYYY-MM-DD HH:MM:SS."}, status=400)

            print("✅ Final Due Date:", due_date_obj)

            # Save the todo
            todo = Todo.objects.create(
                organization=conversation.organization,
                conversation=conversation,
                user=user,
                todo=todo_text,
                type="task",  
                due_date=due_date_obj,
            )
            print("✅ Todo Created Successfully:", todo)
            return JsonResponse({"status": "success", "message": "Todo scheduled successfully!"})

        except Conversation.DoesNotExist:
            print("❌ Conversation Not Found")
            return JsonResponse({"status": "error", "message": "Conversation not found."}, status=400)
        except Exception as e:
            print("❌ Unexpected Error:", str(e))
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)


# /todo manage 
# (MANAGE USERS TODOS )
@csrf_exempt
def fetch_todos(request, org_id, conversation_id):
    user = request.user  # Get the logged-in user
    
    if request.method == "GET":
        # Fetch todos for the given org and conversation
        todos = Todo.objects.filter(organization_id=org_id, conversation_id=conversation_id, user=user)
        todos_data = [
            {
                "id": todo.id,
                "todo": todo.todo,
                "type": todo.type,
                "priority": todo.priority,
                "status": todo.status,
                "reminder": todo.reminder,
                "due_date": todo.due_date.strftime('%Y-%m-%d %H:%M:%S') if todo.due_date else None,
            }
            for todo in todos
        ]
        return JsonResponse({"status": "success", "todos": todos_data})
    
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)


# Update todos 
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def update_todo(request, org_id, conversation_id, todo_id):
    user = request.user  # Get the logged-in user
    
    if request.method == "POST":
        try:
            # Log the request body
            logger.debug(f"Request body: {request.body}")
            
            data = json.loads(request.body)
            
            todo = get_object_or_404(Todo, id=todo_id, user=user, organization_id=org_id, conversation_id=conversation_id)
            
            todo.status = data.get("status", todo.status)
            todo.priority = data.get("priority", todo.priority)
            todo.type = data.get("type", todo.type)
            todo.reminder = data.get("reminder", todo.reminder)
            
            if data.get("due_date"):
                todo.due_date = data.get("due_date")
            
            todo.save()
            
            return JsonResponse({"status": "success", "message": "Todo updated successfully."})
        
        except Exception as e:
            logger.error(f"Error: {e}")  
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)


# delete todo

@csrf_exempt
def delete_todo(request, org_id, conversation_id, todo_id):
    user = request.user 
    
    if request.method == "POST":
        try:
            todo = get_object_or_404(Todo, id=todo_id, user=user, organization_id=org_id, conversation_id=conversation_id)
            todo.delete()
            return JsonResponse({"status": "success", "message": "Todo deleted successfully."})
        
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)


# /meme (GENERATES RANDOM MEME USING MEME API)
def get_random_meme(request):
    url = "https://meme-api.com/gimme"
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")  # Print status code
        print(f"Response Headers: {response.headers}")  # Print response headers
        print(f"Response Content: {response.content}")  # Print raw content

        response.raise_for_status()  # Raises HTTPError for bad responses

        data = response.json()
        print(f"JSON Data: {data}")  # Print JSON data

        if "url" in data:
            return JsonResponse({"status": "success", "meme_url": data["url"]})
        else:
            print("No 'url' in JSON response.")
            return JsonResponse({"status": "error", "message": "No meme URL found in response."})

    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")
        return JsonResponse({"status": "error", "message": f"API request error: {str(e)}"})
    except ValueError as ve:
        print(f"JSON Decode Error: {ve}")
        return JsonResponse({"status": "error", "message": "Invalid JSON response from API."})
    


# /DEFINE <WORD>/

def get_definition(request, word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        definition = data[0]['meanings'][0]['definitions'][0]['definition']
        return JsonResponse({"status": "success", "word": word, "definition": definition})
    else:
        return JsonResponse({"status": "error", "message": "Definition not found"})



# /docs <tech> (FETCH DOCUMENTATION ABOUT TECHSTACK)
@csrf_exempt
def fetch_docs(request, tech):
    url = "https://devdocs.io/docs.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise error if bad response

        all_docs = response.json()
        tech_docs = [f"https://devdocs.io/{doc['slug']}" for doc in all_docs if tech.lower() in doc['slug'].lower()]
        
        if tech_docs:
            return JsonResponse({"docs": tech_docs})
        else:
            return JsonResponse({"error": "Documentation not found"}, status=404)
    
    except requests.exceptions.RequestException:
        return JsonResponse({"error": "Failed to fetch documentation"}, status=500)



# /ROAST 
from .roasts import ROASTS


def fetch_roast(request):
    roast = random.choice(ROASTS)
    return JsonResponse({"roast": roast})


# /ping (current network status)
import subprocess
import speedtest
import psutil
import time

def get_ping():
    """Ping Google's DNS (8.8.8.8) and return the response time in ms."""
    try:
        result = subprocess.run(["ping", "-c", "4", "8.8.8.8"], capture_output=True, text=True)
        lines = result.stdout.split("\n")
        stats = lines[-2].split("=")[-1].strip().split("/")
        return {"min": float(stats[0]), "avg": float(stats[1]), "max": float(stats[2])}
    except Exception:
        return {"min": None, "avg": None, "max": None}

def get_network_speed():
    """Get download and upload speed using speedtest library."""
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = round(st.download() / 1_000_000, 2)  # Convert to Mbps
        upload_speed = round(st.upload() / 1_000_000, 2)  # Convert to Mbps
        return {"download_speed": download_speed, "upload_speed": upload_speed}
    except Exception:
        return {"download_speed": None, "upload_speed": None}

def get_system_uptime():
    """Get system uptime in hours and minutes."""
    uptime_seconds = time.time() - psutil.boot_time()
    uptime_hours = int(uptime_seconds // 3600)
    uptime_minutes = int((uptime_seconds % 3600) // 60)
    return f"{uptime_hours}h {uptime_minutes}m"

def get_cpu_usage():
    """Get CPU usage percentage."""
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    """Get memory usage percentage."""
    memory_info = psutil.virtual_memory()
    return memory_info.percent

def get_disk_usage():
    """Get disk usage percentage."""
    disk_info = psutil.disk_usage('/')
    return disk_info.percent

def get_active_processes():
    """Get the number of active processes."""
    return len(psutil.pids())

def get_network_usage():
    """Get network sent/received data in MB."""
    net_io = psutil.net_io_counters()
    return {
        "sent": round(net_io.bytes_sent / (1024 * 1024), 2),  # Convert to MB
        "received": round(net_io.bytes_recv / (1024 * 1024), 2),  # Convert to MB
    }

def fetch_ping_stats(request):
    """
    Returns real-time server response times, network speed, system uptime, API latency,
    CPU usage, memory usage, disk usage, active processes, and network usage.
    """
    ping_data = get_ping()
    speed_data = get_network_speed()
    uptime = get_system_uptime()
    cpu_usage = get_cpu_usage()
    memory_usage = get_memory_usage()
    disk_usage = get_disk_usage()
    active_processes = get_active_processes()
    network_usage = get_network_usage()
    
    data = {
        "server_response_times": ping_data,  
        "network_speed": speed_data,  
        "system_uptime": uptime,  
        "api_latency": [random.randint(100, 500) for _ in range(7)],  
        "cpu_usage": cpu_usage, 
        "memory_usage": memory_usage,
        "disk_usage": disk_usage, 
        "active_processes": active_processes, 
        "network_usage": network_usage,  
    }
    return JsonResponse(data)


# /wiki <query>
def fetch_wikipedia(request):
    query = request.GET.get("query", "").strip()
    
    if not query:
        return JsonResponse({"error": "No query provided"}, status=400)
    
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return JsonResponse(response.json())
    else:
        return JsonResponse({"error": "Failed to fetch Wikipedia data"}, status=500)


# /github <username>



GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
GITHUB_ACCESS_TOKEN = settings.GITHUB_ACCESS_TOKEN  

def fetch_github_user(request):
    username = request.GET.get("username")
    print("USERNAME RECIVED:",username)
    if not username:
        return JsonResponse({"error": "Username is required"}, status=400)

    query = """
    {
        user(login: "%s") {
            name
            login
            avatarUrl
            bio
            location
            websiteUrl
            followers {
                totalCount
            }
            following {
                totalCount
            }
            repositories(first: 10, orderBy: {field: STARGAZERS, direction: DESC}) {
                nodes {
                    name
                    description
                    url
                    stargazers {
                        totalCount
                    }
                }
            }
        }
    }
    """ % username

    headers = {
        "Authorization": f"Bearer {GITHUB_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(GITHUB_GRAPHQL_URL, json={"query": query}, headers=headers)

    if response.status_code == 200:
        return JsonResponse(response.json().get("data", {}))
    else:
        return JsonResponse({"error": "Failed to fetch data"}, status=response.status_code)
    



# /generate <topic>
from openai import OpenAI
from django.http import JsonResponse

client = OpenAI(api_key="#")

def generate_content(request):
    topic = request.GET.get("topic", "")
    if not topic:
        return JsonResponse({"error": "No topic provided"}, status=400)

    prompt = f"Write a detailed blog post about {topic}."
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content.strip()
    return JsonResponse({"content": content})



# /code <topic> <language> 
def generate_code(request):
    topic = request.GET.get("topic", "").strip()
    language = request.GET.get("language", "").strip()

    if not topic or not language:
        return JsonResponse({"error": "Invalid request. Provide both topic and language."}, status=400)

    try:
        prompt = f"Write a {language} code snippet for {topic} with proper syntax and best practices."
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[{"role": "user", "content": prompt}]
        )

        code = response.choices[0].message.content

        return JsonResponse({"code": code, "language": language})
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



# /ai (HANDLE REAL TIME AI QUERIES)
client = OpenAI(api_key="#")  


import re


# PENDING AI OPTIMIZATION

@csrf_exempt
@login_required
def ai_chat_view(request, org_id, conversation_id, other_user_id):
    organization = get_object_or_404(Organization, id=org_id)
    conversation = get_object_or_404(Conversation, id=conversation_id, organization=organization)
    other_user = get_object_or_404(User, id=other_user_id)

    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "").strip().lower()
        user = request.user

        if not user_message:
            return JsonResponse({"error": "Message cannot be empty"}, status=400)

        # Determine intent using NLP
        intent, entity = analyze_intent(user_message)

        if intent in ["create", "update", "delete", "read"]:
            result = handle_crud_operation(intent, entity, user, organization, conversation)
            return JsonResponse({"response": result})
        
        # General AI Chat Response
        context_data = generate_context(user, organization, conversation)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[
                {"role": "system", "content": "This is the calendar Plus webapp built by django for team management & real time scheduling software, and you are the main character AI of CalendarPlus , users will interact with you to know about their meetings, events, todos and more and you have to provide valid answers to them and also give Welcome to CalendarPlus Message|You are an AI assistant helping users manage meetings, tasks, and events in Calendar Plus."},
                {"role": "user", "content": f"User Query: {user_message}\n\nContext: {context_data}"}
            ]
        )
        ai_response = response.choices[0].message.content.strip()
        return JsonResponse({"response": ai_response})

    return JsonResponse({"error": "Invalid request"}, status=400)

# Analyze user intent using basic NLP (can be replaced with an AI model)
def analyze_intent(user_message):
    words = user_message.split()
    
    if "add" in words or "create" in words:
        return "create", extract_entity(user_message)
    elif "update" in words or "edit" in words:
        return "update", extract_entity(user_message)
    elif "delete" in words or "remove" in words:
        return "delete", extract_entity(user_message)
    elif "show" in words or "fetch" in words:
        return "read", extract_entity(user_message)
    
    return "chat", None  # Default to chat if no intent is detected

# Extract relevant entity (meeting, todo, etc.) from user input
def extract_entity(user_message):
    entities = ["meeting", "todo", "task", "event", "message"]
    for entity in entities:
        if entity in user_message:
            return entity
    return None

# Perform CRUD operations based on intent and entity
def handle_crud_operation(intent, entity, user, organization, conversation):
    if entity == "meeting":
        return handle_meeting_crud(intent, user, organization)
    elif entity == "todo" or entity == "task":
        return handle_todo_crud(intent, user, organization, conversation)
    elif entity == "event":
        return handle_event_crud(intent, user, organization)
    elif entity == "message":
        return handle_message_crud(intent, user, organization, conversation)
    
    return "I couldn't understand what you want to do. Please try again!"

# CRUD Functions for Different Entities
def handle_meeting_crud(intent, user, organization):
    if intent == "create":
        MeetingOrganization.objects.create(user=user, organization=organization, meeting_title="New Meeting")
        return "Meeting created successfully."
    elif intent == "update":
        meeting = MeetingOrganization.objects.filter(user=user, organization=organization).first()
        if meeting:
            meeting.meeting_title = "Updated Meeting"
            meeting.save()
            return "Meeting updated successfully."
        return "No meeting found to update."
    elif intent == "delete":
        MeetingOrganization.objects.filter(user=user, organization=organization).delete()
        return "Meeting deleted successfully."
    elif intent == "read":
        meetings = MeetingOrganization.objects.filter(user=user, organization=organization)
        return "Your meetings: " + ", ".join(m.meeting_title for m in meetings) if meetings else "No meetings found."

    return "Invalid meeting operation."

def handle_todo_crud(intent, user, organization, conversation):
    if intent == "create":
        Todo.objects.create(user=user, organization=organization, conversation=conversation, todo="New Task")
        return "Task added successfully."
    elif intent == "update":
        todo = Todo.objects.filter(user=user, organization=organization, conversation=conversation).first()
        if todo:
            todo.todo = "Updated Task"
            todo.save()
            return "Task updated successfully."
        return "No task found to update."
    elif intent == "delete":
        Todo.objects.filter(user=user, organization=organization, conversation=conversation).delete()
        return "Task deleted successfully."
    elif intent == "read":
        todos = Todo.objects.filter(user=user, organization=organization, conversation=conversation)
        return "Your tasks: " + ", ".join(t.todo for t in todos) if todos else "No tasks found."

    return "Invalid task operation."

def handle_event_crud(intent, user, organization):
    if intent == "create":
        EventOrganization.objects.create(user=user, organization=organization, title="New Event")
        return "Event created successfully."
    elif intent == "update":
        event = EventOrganization.objects.filter(user=user, organization=organization).first()
        if event:
            event.title = "Updated Event"
            event.save()
            return "Event updated successfully."
        return "No event found to update."
    elif intent == "delete":
        EventOrganization.objects.filter(user=user, organization=organization).delete()
        return "Event deleted successfully."
    elif intent == "read":
        events = EventOrganization.objects.filter(user=user, organization=organization)
        return "Your events: " + ", ".join(e.title for e in events) if events else "No events found."

    return "Invalid event operation."

def handle_message_crud(intent, user, organization, conversation):
    if intent == "create":
        Message.objects.create(sender=user, organization=organization, conversation=conversation, text="New Message")
        return "Message sent successfully."
    elif intent == "delete":
        Message.objects.filter(sender=user, organization=organization, conversation=conversation).delete()
        return "Message deleted successfully."
    elif intent == "read":
        messages = Message.objects.filter(sender=user, organization=organization, conversation=conversation)
        return "Your messages: " + ", ".join(m.text for m in messages) if messages else "No messages found."
    
    return "Invalid message operation."


# ✅ **Generate Full Context for AI**
def generate_context(user, organization, conversation):
    """Fetch and structure user-specific data for AI to process."""

    meetings = MeetingOrganization.objects.filter(user=user, organization=organization).values("meeting_title", "meeting_date", "start_time")
    todos = Todo.objects.filter(user=user, conversation=conversation, organization=organization).values("todo", "priority", "status")
    messages = Message.objects.filter(sender=user, organization=organization, conversation=conversation).values("text", "timestamp")
    latest_events = EventOrganization.objects.filter(user=user, organization=organization).order_by('-created_at')[:4]

    # 🔹 **Structuring the data for AI**
    formatted_meetings = "\n".join([f"📅 {m['meeting_title']} on {m['meeting_date']} at {m['start_time']}" for m in meetings]) or "No meetings found."
    formatted_todos = "\n".join([f"✅ {t['todo']} (Priority: {t['priority']}, Status: {t['status']})" for t in todos]) or "No todos found."
    formatted_messages = "\n".join([f"💬 {m['text']} (Sent at: {m['timestamp']})" for m in messages]) or "No messages found."
    formatted_events = get_latest_events_formatted(latest_events)

    return (
        f"User's Data:\n"
        f"📌 Meetings:\n{formatted_meetings}\n\n"
        f"📝 Todos:\n{formatted_todos}\n\n"
        f"💬 Messages:\n{formatted_messages}\n\n"
        f"🎉 Latest Events:\n{formatted_events}"
    )


# ✅ **Fetch Latest 4 Events and Format**
def get_latest_events_formatted(events):
    count = events.count()
    if count == 0:
        return "🔍 No recent events found."

    response = f"🎉 **I found {count} of your most recent events:**\n\n"
    for idx, event in enumerate(events, start=1):
        response += (
            f"🔹 **Event {idx}:**\n"
            f"   📖 **Title**: {event.title}\n"
            f"   📂 **Type**: {event.event_type}\n"
            f"   📝 **Description**: {event.description}\n"
            f"   ⏳ **Duration**: {event.duration}\n"
            f"   📍 **Location**: {event.location}\n"
            f"   📅 **Created On**: {event.created_at.strftime('%B %d, %Y')}\n"
            f"   -----------------------------------\n"
        )

    return response + "💡 Need more details? Just let me know! 🚀"



# InChat Reminders 
# /remind <what> <when>

@csrf_exempt
@login_required
def save_reminder(request, org_id, conversation_id=None):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user
            text = data.get("text")
            remind_at = data.get("remind_at")  

            if not (text and remind_at):
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Validate organization
            try:
                organization = Organization.objects.get(id=org_id)
            except Organization.DoesNotExist:
                return JsonResponse({"error": "Invalid organization"}, status=400)

            # Validate conversation (optional)
            conversation = None
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                except Conversation.DoesNotExist:
                    return JsonResponse({"error": "Invalid conversation"}, status=400)

            # Convert remind_at to datetime object
            try:
                remind_at_dt = datetime.strptime(remind_at, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return JsonResponse({"error": "Invalid date format"}, status=400)

            # Create and save reminder
            reminder = Reminder.objects.create(
                user=user,
                organization=organization,
                conversation=conversation,
                text=text,
                remind_at=remind_at_dt
            )

            return JsonResponse({"success": True, "message": "Reminder saved successfully!"}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


# /security check - scan the entire system
import subprocess
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

VIRUSTOTAL_API_KEY = "#"

@csrf_exempt
def security_check_view(request):
    if request.method == "GET":
        # 1️⃣ Open Ports Check
        open_ports = subprocess.getoutput("netstat -tuln").split("\n")[2:]

        # 2️⃣ Outdated Software Check
        outdated_software = subprocess.getoutput("apt list --upgradable").split("\n")[1:]

        # 3️⃣ System Uptime
        system_uptime = subprocess.getoutput("uptime -p")

        # 4️⃣ Suspicious Processes
        suspicious_processes = subprocess.getoutput("ps aux | grep -i 'cryptominer'").split("\n")

        # 5️⃣ Active Network Connections
        network_connections = subprocess.getoutput("netstat -an").split("\n")

        # 6️⃣ Firewall Status
        firewall_status = subprocess.getoutput("ufw status")

        # 7️⃣ Running Services
        running_services = subprocess.getoutput("systemctl list-units --type=service --state=running").split("\n")

        # 8️⃣ File Integrity Check (Example: Check for root file modifications)
        file_integrity = subprocess.getoutput("ls -lah /root/")

        # 9️⃣ Rootkit Detection
        rootkit_check = subprocess.getoutput("chkrootkit | grep INFECTED")

        # 🔟 Unused Users & SSH Keys
        unused_users = subprocess.getoutput("awk -F: '{ if ($3 >= 1000) print $1}' /etc/passwd").split("\n")

        # 🛡 Malware Check (VirusTotal API)
        malware = False
        headers = {"x-apikey": VIRUSTOTAL_API_KEY}
        response = requests.get("https://www.virustotal.com/api/v3/files", headers=headers)
        if response.status_code == 200 and "malicious" in response.text:
            malware = True

        return JsonResponse({
            "open_ports": open_ports,
            "outdated_software": outdated_software,
            "system_uptime": system_uptime,
            "suspicious_processes": suspicious_processes,
            "network_connections": network_connections,
            "firewall_status": firewall_status,
            "running_services": running_services,
            "file_integrity": file_integrity,
            "rootkit_check": rootkit_check,
            "unused_users": unused_users,
            "malware": malware
        })

@csrf_exempt
def fix_security_issues(request):
    if request.method == "POST":
        # Close open ports (Example: Closing port 22)
        if os.name != "nt":  # Linux/macOS
            subprocess.run(["ufw", "deny", "22"])

        # Upgrade software
        if os.name == "nt":  # Windows
            subprocess.run(["powershell", "Get-WindowsUpdate"])
        else:
            subprocess.run(["apt", "update"])
            subprocess.run(["apt", "upgrade", "-y"])

        return JsonResponse({"status": "success", "message": "Security issues fixed!"})


# /Export the data
from django.core.mail import EmailMessage
from django.http import HttpResponse
import json
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

@login_required
@csrf_exempt
def export_messages_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            conversation_id = data.get("conversation_id")
            org_id = data.get("org_id")
            export_type = data.get("export_type")
            custom_email = data.get("custom_email", None)

            conversation = get_object_or_404(Conversation, id=conversation_id, organization_id=org_id)
            messages = Message.objects.filter(conversation=conversation).order_by("timestamp")

            if not messages.exists():
                return JsonResponse({"error": "No messages found."}, status=404)

            # Prepare data
            csv_data = [["Sender", "Text", "File", "Timestamp"]]
            for msg in messages:
                csv_data.append([
                    msg.sender.username,
                    msg.text if msg.text else "N/A",
                    msg.file.url if msg.file else "No File",
                    msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                ])

            csv_content = "\n".join([",".join(row) for row in csv_data])

            # Handle export formats
            if export_type in ["email", "input-email"]:
                email = request.user.email if export_type == "email" else custom_email
                if not email:
                    return JsonResponse({"error": "No email provided."}, status=400)

                email_message = EmailMessage(
                    subject="Exported Chat Messages",
                    body="Attached is the exported chat data.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email],
                )
                email_message.attach("exported_messages.csv", csv_content, "text/csv")
                email_message.send()
                return JsonResponse({"message": f"Chat data sent to {email}!"})

            elif export_type == "csv":
                response = HttpResponse(csv_content, content_type="text/csv")
                response["Content-Disposition"] = 'attachment; filename="exported_messages.csv"'
                return response

            elif export_type == "pdf":
                # Generate PDF using ReportLab
                buffer = io.BytesIO()
                pdf_canvas = canvas.Canvas(buffer, pagesize=letter)
                pdf_canvas.setTitle("Chat Messages Export")

                y = 750  # Start position on PDF
                pdf_canvas.setFont("Helvetica-Bold", 14)
                pdf_canvas.drawString(200, y, "Chat Messages Export")
                pdf_canvas.setFont("Helvetica", 12)

                y -= 30
                for row in csv_data[1:]:
                    pdf_canvas.drawString(50, y, f"{row[0]}: {row[1]} ({row[3]})")
                    y -= 20
                    if y < 50:  # Avoid writing out of bounds
                        pdf_canvas.showPage()
                        pdf_canvas.setFont("Helvetica", 12)
                        y = 750

                pdf_canvas.save()
                buffer.seek(0)

                response = HttpResponse(buffer, content_type="application/pdf")
                response["Content-Disposition"] = 'attachment; filename="exported_messages.pdf"'
                return response

            elif export_type == "drive":
                return JsonResponse({"message": "File uploaded to Google Drive!"})

            elif export_type == "dropbox":
                return JsonResponse({"message": "File uploaded to Dropbox!"})

            elif export_type == "slack":
                return JsonResponse({"message": "File sent to Slack!"})

            return JsonResponse({"error": "Invalid export type."}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)


# /panic-delete <minutes> -- delete messages for tht minutes

@login_required
@csrf_exempt
def panic_delete_messages(request):
    if request.method == "POST":
        org_id = request.POST.get("org_id")
        conversation_id = request.POST.get("conversation_id")
        minutes = int(request.POST.get("minutes", 0))
        
        if not org_id or not conversation_id or minutes <= 0:
            return JsonResponse({"success": False, "error": "Invalid data"}, status=400)
        
        try:
            cutoff_time = now() - timedelta(minutes=minutes)
            messages_deleted = Message.objects.filter(
                sender=request.user, 
                conversation_id=conversation_id, 
                timestamp__gte=cutoff_time
            ).delete()

            return JsonResponse({"success": True, "deleted_count": messages_deleted[0]})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
