from django.shortcuts import render,redirect,get_list_or_404,get_object_or_404
from .models import MiniApp,InstalledMiniApp
from accounts.models import (Organization, Profile,MeetingOrganization,MeetingNotes)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from django.utils.timezone import localtime
from .check_org_membership import check_org_membership
from groups.models import (GroupMember)
from django.utils.timezone import now
# Create your views here.

# Display Miniapps 
def mini_apps_list(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)
    
    # Fetch all apps once
    apps_queryset = MiniApp.objects.order_by('-install_count')

    # Explicitly create separate querysets to avoid duplicates
    categories = {
        "All": list(apps_queryset),  # Convert to list to prevent shared references
        "Productivity": list(apps_queryset.filter(category="productivity")),
        "Communication": list(apps_queryset.filter(category="communication")),
        "Task Management": list(apps_queryset.filter(category="task_management")),
        "Entertainment": list(apps_queryset.filter(category="entertainment")),
        "Utility": list(apps_queryset.filter(category="utility")),
        "Other": list(apps_queryset.filter(category="other")),
    }

    return render(request, "mini_apps/purchase/dashboard.html", {
        "categories": categories,
        "organization": organization
    })


# INSTALLATION PAGE
def mini_app_detail(request, app_id, org_id):
    organization = get_object_or_404(Organization, id=org_id)
    app = get_object_or_404(MiniApp, id=app_id)

    # Check if the app is already installed for this organization
    is_installed = InstalledMiniApp.objects.filter(organization=organization, mini_app=app).exists()

    return render(request, "mini_apps/install/detail.html", {
        "app": app,
        "organization": organization,
        "is_installed": is_installed  
    })


# INSTALL MINI-APP
@csrf_exempt  
@login_required
def install_mini_app(request):
    if request.method == "POST":
        org_id = request.POST.get("org_id")
        app_id = request.POST.get("app_id")

        if not org_id or not app_id:
            return JsonResponse({"success": False, "message": "Missing organization or app ID"}, status=400)

        organization = get_object_or_404(Organization, id=org_id)
        mini_app = get_object_or_404(MiniApp, id=app_id)
        user = request.user

        # Check if already installed
        if InstalledMiniApp.objects.filter(user=user, organization=organization, mini_app=mini_app).exists():
            return JsonResponse({"success": False, "message": "App already installed"}, status=400)

        # Install the app
        InstalledMiniApp.objects.create(user=user, organization=organization, mini_app=mini_app)
        mini_app.install_count+=1
        mini_app.save()
        return JsonResponse({"success": True, "message": "App installed successfully"})

    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)



# LAUNCH APP
@login_required
def launch_app(request,org_id,app_id):
    organization = get_object_or_404(Organization,id=org_id)
    app=get_object_or_404(InstalledMiniApp,id=app_id)
    if not app:
        return JsonResponse({'error:':'App not Found!'},status=401)
    
    profile = get_object_or_404(Profile,organization=organization,user=request.user)
    if not profile:
        return JsonResponse({'error:':'You are not authorized to launch the app'},status=400)
    
    context = {
        "app":app,
        "organization":organization
    }
    
    return render(request,'mini_apps/launch/launch.html',context)

# ------------------------------------------------------------------------------------------------------------------------------
# APPS (TASK MANAGER - KANBAN BOARD)
from .models import TaskManager
import json 

# Add task
@csrf_exempt
@login_required
def add_task_view_workspace(request, org_id, app_id):
    print(f"✅ Received request at add_task_view with org_id={org_id}, app_id={app_id}")
    """Handles task creation via AJAX with JSON body."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON request body
            print("DATA:",data)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        # Debug: Print org_id and app_id to check if they are correct
        print(f"Received org_id: {org_id}, app_id: {app_id}")

        # Fetch Organization and MiniApp
        organization = get_object_or_404(Organization,id=org_id)
        app = get_object_or_404(InstalledMiniApp, id=int(app_id))

        organization=get_object_or_404(Organization, id=org_id)
        profile=get_object_or_404(Profile,organization=organization,user=request.user)
        if not profile:
          return JsonResponse({'error:':'You are not authorized to perform this action!'})


        if not app:
          return HttpResponseBadRequest("Invalid app ID")


        if not app.mini_app.commands or "/add task" not in app.mini_app.commands:
           return HttpResponseBadRequest("Error")

        # Debug: Print if organization and mini_app are found
        print(f"Found Organization: {organization.name}, Found MiniApp: {app.mini_app.name}")

      
        # Get task details from JSON
        task_title = data.get("title", "").strip()
        task_description = data.get("description", "").strip()
        task_status = data.get("status", "todo")  # Default: 'To Do'

        if not task_title:
            return JsonResponse({"error": "Task title is required!"}, status=400)

        # Create the task
        task = TaskManager.objects.create(
            organization=organization,
            title=task_title,
            description=task_description,
            status=task_status,
            assigned_to=request.user
        )

        # Return success response with task data
        return JsonResponse({
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status
            }
        })

    return JsonResponse({"error": "Invalid request"}, status=400)



# KANBAN BOARD HANDLING
@login_required
def get_tasks_kanban(request, org_id, app_id):
    organization= get_object_or_404(Organization, id=org_id)
    print(f"Received app_id: {app_id}")

    organization=get_object_or_404(Organization, id=org_id)
    profile=get_object_or_404(Profile,organization=organization,user=request.user)
    if not profile:
        return JsonResponse({'error:':'You are not authorized to perform this action!'})



    app = get_object_or_404(InstalledMiniApp, id=int(app_id))

    if not app:
       return HttpResponseBadRequest("Invalid app ID")


    if not app.mini_app.commands or "/open kanban" not in app.mini_app.commands:
        return HttpResponseBadRequest("Error")


    
    """ Fetch all tasks where request.user is assigned_to and the task belongs to the given app_id """
    
    # Fetch tasks ensuring they belong to the correct org and assigned user
    tasks = TaskManager.objects.filter(
        organization=organization,
        assigned_to=request.user
    ).values("id", "title", "status")  # Optimized query
    print("TASKS FOUND:",tasks)

    tasks_list = list(tasks)  # Convert QuerySet to a list

    if not tasks_list:
        print(f"No tasks found for user {request.user} in org {organization.name} and app {app_id}")  # Debugging

    return JsonResponse({"tasks": tasks_list}, safe=False)







# Update tasks in kanban
@csrf_exempt
@login_required
def update_task_status(request):
    """ Update task status when user moves task in Kanban """
    if request.method == "POST":
        task_id = request.POST.get("task_id")
        new_status = request.POST.get("status")

        task = get_object_or_404(TaskManager, id=task_id, assigned_to=request.user)
        task.status = new_status
        task.save()

        return JsonResponse({"success": True, "message": "Task status updated!"})

    return JsonResponse({"success": False, "message": "Invalid request!"})

# DELETE THE TASK
@csrf_exempt
def delete_task(request):
    if request.method == "POST":
        task_id = request.POST.get("task_id")
        if not task_id:
            return JsonResponse({"success": False, "error": "Task ID missing!"})
        
        try:
            task = TaskManager.objects.get(id=task_id)
            task.delete()  # Delete the task
            return JsonResponse({"success": True})
        except TaskManager.DoesNotExist:
            return JsonResponse({"success": False, "error": "Task not found!"})
    
    return JsonResponse({"success": False, "error": "Invalid request method!"})

# Get task details
def task_details(request, task_id):
    """Fetch and return task details as JSON (GET request only)."""
    if request.method != "GET":
        return HttpResponseBadRequest("Invalid request method. Only GET is allowed.")

    task = get_object_or_404(TaskManager, id=task_id)

    data = {
        "success": True,
        "title": task.title,
        "description": task.description or "No description provided",
        "created_by": task.assigned_to.username if task.assigned_to else "Unknown",
        "due_date": "Nothing To Display",
    }
    return JsonResponse(data)
# ------------------------------------------------------------------------------------------------------------------------------


# CHANNELS -------
from organization_channels.models import Channel, Message,ActivityChannel,Link,ChannelAccess,ChannelEvents,Ban,RetentionPolicy
from django.core.mail import EmailMessage
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse

# FETCH CHANNELS 
@login_required
def get_workspace_channels(request):
    org_id = request.GET.get("org_id")
    app_id = request.GET.get("app_id")

    organization=get_object_or_404(Organization, id=org_id)
    profile=get_object_or_404(Profile,organization=organization,user=request.user)
    if not profile:
        return JsonResponse({'error:':'You are not authorized to perform this action!'})


    if not org_id or not app_id:
        return JsonResponse({"success": False, "error": "Missing org_id or app_id"})

    channels = Channel.objects.filter(organization_id=org_id).values("id", "name")

    if channels.exists():
        return JsonResponse({"success": True, "channels": list(channels)})
    else:
        return JsonResponse({"success": False, "channels": []})
    

# CLEAR ALL CHANNEL MESSAGES 

@login_required
def delete_all_messages(request):
    channel_id = request.GET.get("channel_id")
    org_id = request.GET.get("org_id")

    organization=get_object_or_404(Organization, id=org_id)
    profile=get_object_or_404(Profile,organization=organization,user=request.user)
    if not profile:
        return JsonResponse({'error:':'You are not authorized to perform this action!'})

    if not channel_id or not org_id:
        return JsonResponse({"success": False, "error": "Missing channel_id or org_id"}, status=400)

    # Get the channel and organization
    channel = get_object_or_404(Channel, id=channel_id, organization_id=org_id)


    # Delete all messages in the channel
    Message.objects.filter(channel=channel,organization=organization,user=request.user).delete()

    return JsonResponse({"success": True, "message": "All messages deleted successfully!"})



# DOWNLOAD CHANNEL DATA
@check_org_membership
def export_channels(request, org_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=400)

    try:
        data = json.loads(request.body)
        action = data.get("action")  # "download" or "email"
        user_email = data.get("email")  # Email if the user chooses to send it

        channels = Channel.objects.filter(organization_id=org_id)
        if not channels.exists():
            return JsonResponse({"error": "No channels found in this organization."}, status=400)

        # Generate PDF
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        pdf.setTitle("Organization Channels Report")

        y_position = 800  # Start position for content
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(200, y_position, "Organization Channels Report")
        y_position -= 30

        for channel in channels:
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(50, y_position, f"Channel: {channel.name} ({channel.get_visibility_display()})")
            y_position -= 20
            pdf.setFont("Helvetica", 12)

            # Messages
            messages = Message.objects.filter(channel=channel)
            pdf.drawString(50, y_position, f"Total Messages: {messages.count()}")
            y_position -= 20
            for message in messages[:5]:  # Show only 5 messages for readability
                pdf.drawString(70, y_position, f"- {message.user.username}: {message.content[:50]}...")
                y_position -= 15

            # Links
            links = Link.objects.filter(channel=channel)
            pdf.drawString(50, y_position, f"Total Links: {links.count()}")
            y_position -= 20
            for link in links[:5]:
                pdf.drawString(70, y_position, f"- {link.text}: {link.link}")
                y_position -= 15

            # Activities
            activities = ActivityChannel.objects.filter(channel=channel)
            pdf.drawString(50, y_position, f"Total Activities: {activities.count()}")
            y_position -= 20
            for activity in activities[:5]:
                pdf.drawString(70, y_position, f"- {activity.action_type}: {activity.content[:50]}...")
                y_position -= 15

            # Events
            events = ChannelEvents.objects.filter(channel=channel)
            pdf.drawString(50, y_position, f"Total Events: {events.count()}")
            y_position -= 20
            for event in events[:3]:
                pdf.drawString(70, y_position, f"- {event.event_name}: {event.event_details[:50]}...")
                y_position -= 15

            y_position -= 30  # Space before next channel
            if y_position < 100:  # Prevent writing out of bounds
                pdf.showPage()
                y_position = 800

        pdf.save()
        buffer.seek(0)

        # If the user wants to download
        if action == "download":
            response = HttpResponse(buffer, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="channels_report.pdf"'
            return response

        # If the user wants to send via email
        elif action == "email":
            if not user_email:
                return JsonResponse({"error": "Email address is required."}, status=400)

            email = EmailMessage(
                "Organization Channels Report",
                "Attached is your requested report.",
                "no-reply@calendarplus.com",
                [user_email]
            )
            email.attach("channels_report.pdf", buffer.getvalue(), "application/pdf")
            email.send()

            return JsonResponse({"success": "PDF sent successfully to your email."})

        else:
            return JsonResponse({"error": "Invalid action."}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data."}, status=400)
    

# CHANNEL ANALYSIS & OVERVIEW - /overview
@check_org_membership
def get_channels_analytics(request, org_id):
    org = get_object_or_404(Organization, id=org_id)
    channels = Channel.objects.filter(organization=org)

    analytics_data = {
        "labels": [],
        "messages": [],
        "events": [],
        "members": [],
        "banned_users": [],
        "links_shared": [],
        "retention_policy": [],
    }

    for channel in channels:
        analytics_data["labels"].append(channel.name)
        analytics_data["messages"].append(Message.objects.filter(channel=channel).count())
        analytics_data["events"].append(ChannelEvents.objects.filter(channel=channel).count())
        analytics_data["members"].append(ChannelAccess.objects.filter(channel=channel).count())
        analytics_data["banned_users"].append(Ban.objects.filter(channel=channel).count())
        analytics_data["links_shared"].append(Link.objects.filter(channel=channel).count())
        analytics_data["retention_policy"].append(1 if RetentionPolicy.objects.filter(channel=channel) else 0)  # 1 if enabled, 0 if not

    return JsonResponse({"analytics": analytics_data})


# SET CHANNEL MESSAGES EXPIRY
@csrf_exempt
@login_required
def set_org_expiry(request):
    """Sets expiry time for messages in all channels of an organization."""
    if request.method == "POST":
        org_id = request.POST.get("org_id")
        duration = request.POST.get("expiry")
        valid_durations = {"12h": 12, "24h": 24, "7d": 7 * 24}

        if not org_id:
            return JsonResponse({"error": "Organization ID is missing"}, status=400)
        
        if duration not in valid_durations:
            return JsonResponse({"error": "Invalid expiry selection"}, status=400)

        org = get_object_or_404(Organization, id=org_id)
        profile=get_object_or_404(Profile,organization=org,user=request.user)
        if not profile:
            return JsonResponse({'error:':'you are not authorized person!'})
        
        org.set_expiry = duration  # Save selected expiry for the entire org
        org.save()

        return JsonResponse({"success": f"Auto-expiry set to {duration} for all channels!"})
    
    return JsonResponse({"error": "Invalid request"}, status=400)


# OFF CHANNEL EXPIRY
@csrf_exempt
@login_required
def disable_org_expiry(request):
    """Disables expiry for messages in all channels of an organization."""
    if request.method == "POST":
        org_id = request.POST.get("org_id")

        if not org_id:
            return JsonResponse({"error": "Organization ID is missing"}, status=400)

        org = get_object_or_404(Organization, id=org_id)
        profile=get_object_or_404(Profile,organization=org,user=request.user)
        if not profile:
            return JsonResponse({'error:':'you are not authorized!'})

        org.set_expiry = None  
        org.save()

        return JsonResponse({"success": "✅ Auto-expiry disabled for all channels!"})

    return JsonResponse({"error": "Invalid request"}, status=400)

# GET EXPIRY STATUS
@csrf_exempt
@login_required
def get_user_activities(request):
    """Fetches user activities filtered by organization and channel (if provided)."""
    org_id = request.GET.get("org_id")
    channel_id = request.GET.get("channel_id")
   
    if not org_id:
        return JsonResponse({"error": "Organization ID is required"}, status=400)

    # Get organization
    org = get_object_or_404(Organization, id=org_id)
    channel=get_object_or_404(Channel,id=channel_id,organization=org)

    profile=get_object_or_404(Profile,organization=org,user=request.user)
    if not profile:
        return JsonResponse({'error:':'you are not authorized!'})


    # Filter activities by organization and user
    activities = ActivityChannel.objects.filter(user=request.user, organization=org,channel=channel)

    # If channel_id is provided, filter further
    if channel_id:
        channel = get_object_or_404(Channel, id=channel_id, organization=org)
        activities = activities.filter(channel=channel)
    
    # Serialize activity data
    activity_list = [
        {
            "action": activity.get_action_type_display(),
            "content": activity.content,
            "timestamp": activity.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "channel": activity.channel.name if activity.channel else "Organization-wide"
        }
        for activity in activities
    ]

    return JsonResponse({"activities": activity_list}, safe=False)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# A MINI DASHBOARD APP --
# /open dashboard -- launch the dashboard
from accounts.models import MeetingOrganization, EventOrganization,BookingOrganization
from django.utils import timezone
from conversation.models import Conversation,Message
from django.db.models import OuterRef, Subquery, F, Q, Count,Value,CharField
from django.db.models.functions import Concat
from django.conf import settings
from django.contrib.auth.models import User

@check_org_membership
@login_required
@csrf_exempt
def get_dashboard_data(request, org_id):
    """Fetch all dashboard-related data for the given organization and user."""
    user = request.user
    
    # Upcoming Meetings
    upcoming_meetings = MeetingOrganization.objects.filter(
      Q(organization_id=org_id) & 
      (Q(user=request.user) | Q(invitee=request.user)) & 
      Q(meeting_date__gte=timezone.now().date())
    ).order_by('meeting_date', 'start_time').values(
    'id', 'meeting_title', 'meeting_date', 'start_time', 'end_time', 'meeting_link', 'status'
    )
    
    # All Meetings
    all_meetings = MeetingOrganization.objects.filter(
      Q(organization_id=org_id) & 
      (Q(user=request.user) | Q(invitee=request.user))
     ).order_by('-meeting_date', '-start_time').values(
      'id', 'meeting_title', 'meeting_date', 'start_time', 'end_time', 'meeting_link', 'status'
    )
    # Events
    events = EventOrganization.objects.filter(
       Q(organization_id=org_id) & Q(user=request.user)
     ).order_by('-created_at').values(
       'id', 'title', 'event_type', 'location', 'is_recurring', 'created_at'
   )
    # Bookings
    bookings = BookingOrganization.objects.filter(
    Q(organization_id=org_id) & (Q(invitee=request.user) | Q(event_host=request.user))
    ).order_by('-created_at').values(
    'id', 'event__title', 'invitee__username', 'start_time', 'end_time', 'status'
    )
    
    # Groups
    groups = GroupMember.objects.filter(
        organization_id=org_id, user=user
    ).values(
        'id', 'group__name', 'role', 'joined_at'
    )

    # conversations 
    # Fetch conversations where request.user is user1 or user2
    user1_profile_subquery = Profile.objects.filter(
    user=OuterRef('user1'), organization_id=org_id
    ).values('profile_picture')[:1]  

   # Subquery to fetch profile picture for user2
    user2_profile_subquery = Profile.objects.filter(
    user=OuterRef('user2'), organization_id=org_id
    ).values('profile_picture')[:1]  

    # Fetch conversations where request.user is user1 or user2
    conversations = Conversation.objects.filter(
    organization_id=org_id
    ).filter(Q(user1=user) | Q(user2=user)).annotate(
    unread_count=Count("messages", filter=Q(messages__is_read=False) & ~Q(messages__sender=user)),
    
    # Build full profile picture URL
    user1_picture=Concat(Value(settings.MEDIA_URL), Subquery(user1_profile_subquery), output_field=CharField()),
    user2_picture=Concat(Value(settings.MEDIA_URL), Subquery(user2_profile_subquery), output_field=CharField()),
    ).values(
    "id", "user1__username", "user2__username", "unread_count", "user1", "user2", "user1_picture", "user2_picture"
    )

    # users 
   # Subquery to get profile picture for each user
    user_profile_pic_subquery = Profile.objects.filter(
    user=OuterRef('id'), organization_id=org_id
   ).values('profile_picture')[:1]

    # Fetch all users within the same organization along with their profile pictures
    org_users = User.objects.filter(
    profiles__organization_id=org_id
    ).annotate(
    user_profile_pic=Subquery(user_profile_pic_subquery)  # Assigning profile pic to user
    ).values('id', 'username', 'user_profile_pic')

    # Print to check
    for user in org_users:
      print(f"User: {user['username']} | Profile Pic: {user['user_profile_pic']}")

    data = {
        'upcoming_meetings': list(upcoming_meetings),
        'all_meetings': list(all_meetings),
        'events': list(events),
        'bookings': list(bookings),
        'groups': list(groups),
        'conversations':list(conversations),
        "org_users":list(org_users)
    }
    
    return JsonResponse(data, safe=False)


# -----------------------------------------------------------------------------------------------------------------------------------

# MEETING NOTES - /add notes 


@check_org_membership
@csrf_exempt
@login_required
def fetch_user_meetings(request, org_id, user_id):
    """Fetch all meetings where the user is a host, invitee, or participant and categorize them."""
    now = timezone.now().date()

    user_meetings = MeetingOrganization.objects.filter(
        Q(organization_id=org_id) & (
            Q(user_id=user_id) | Q(invitee_id=user_id) | Q(participants__id=user_id)
        )
    ).distinct()

    upcoming_meetings = user_meetings.filter(meeting_date=now, status="scheduled").values(
        'id', 'meeting_title', 'meeting_date', 'start_time', 'end_time', 'status'
    )
    future_meetings = user_meetings.filter(meeting_date__gt=now, status="scheduled").values(
        'id', 'meeting_title', 'meeting_date', 'start_time', 'end_time', 'status'
    )
    past_meetings = user_meetings.filter(meeting_date__lt=now).values(
        'id', 'meeting_title', 'meeting_date', 'start_time', 'end_time', 'status'
    )

    data = {
        "upcoming_meetings": list(upcoming_meetings),
        "future_meetings": list(future_meetings),
        "past_meetings": list(past_meetings),
    }
    return JsonResponse(data, safe=False)

# HANDLE NOTE TAKING 
@csrf_exempt
def add_meeting_note(request):
    """Handles adding and updating notes for a specific meeting."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            meeting_id = data.get("meeting_id")
            org_id = data.get("org_id")
            user_id = data.get("user_id")
            content = data.get("content", "").strip()

            print("RECIEVED ORG_ID:",org_id)

            if not meeting_id or not org_id or not user_id or not content:
                return JsonResponse({"error": "All fields are required!"}, status=400)
            
            profile = get_object_or_404(Profile,organization=organization,user=request.user)
            if not profile:
                return JsonResponse({'error':'you are not authorized!'}, status=400)

            meeting = MeetingOrganization.objects.get(id=meeting_id, organization_id=org_id)
            organization = Organization.objects.get(id=org_id)
            user = User.objects.get(id=user_id)

            # Check if a note already exists for this meeting
            note, created = MeetingNotes.objects.get_or_create(
                organization=organization, meeting=meeting
            )
            note.content = content  # Update content
            note.save()

            return JsonResponse({"message": "Note saved successfully!", "note_id": note.id})
        
        except MeetingOrganization.DoesNotExist:
            return JsonResponse({"error": "Meeting not found!"}, status=404)
        except Organization.DoesNotExist:
            return JsonResponse({"error": "Organization not found!"}, status=404)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found!"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data!"}, status=400)
    return JsonResponse({"error": "Invalid request!"}, status=405)