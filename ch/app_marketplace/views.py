from django.shortcuts import render,redirect,get_list_or_404,get_object_or_404
from .models import (MiniApp,InstalledMiniApp,Bookmark,FileUploadMania)
from accounts.models import (Organization, Profile,MeetingOrganization,MeetingNotes)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from django.utils.timezone import localtime
from .check_org_membership import check_org_membership
from groups.models import (GroupMember)
from django.utils.timezone import now
import os
import uuid
from django.utils.timezone import now, timedelta
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.http import FileResponse, Http404
from django.conf import settings
from django.urls import reverse
# Create your views here.

# Display Miniapps 
@check_org_membership
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
    is_installed = InstalledMiniApp.objects.filter(user=request.user,organization=organization, mini_app=app).exists()

    profile=get_object_or_404(Profile,organization=organization,user=request.user)
    if not profile:
        return JsonResponse({'error:':'You are not authorized!'})

    

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



# LAUNCH APP------------------------------------------------------------------------------------------------------MAIN ---------
@login_required
@check_org_membership
def launch_app(request,org_id,app_id):
    organization = get_object_or_404(Organization,id=org_id)
    app=get_object_or_404(InstalledMiniApp,id=app_id)
    if not app:
        return JsonResponse({'error:':'App not Found!'},status=401)
    
    profile = get_object_or_404(Profile,organization=organization,user=request.user)
    if not profile:
        return JsonResponse({'error:':'You are not authorized to launch the app'},status=400)
    
    # GUI APP share mania
    if "Share Mania" in app.mini_app.name:
       return redirect(reverse_lazy('share_mania_app', kwargs={'org_id': organization.id, 'app_id': app.id}))
    
    # automate scheduling
    elif "Automate Scheduling" in app.mini_app.name:
        return redirect(reverse_lazy('automate_scheduling',kwargs={'org_id':organization.id,'app_id':app.id}))


    context = {
        "app":app,
        "organization":organization
    }
    
    return render(request,'mini_apps/launch/launch.html',context)


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# SHARE MANIA GRAPHICAL USER INTERFACE
@login_required
@check_org_membership
def share_mania(request,org_id,app_id):
    organization = get_object_or_404(Organization,id=org_id)
    app=get_object_or_404(InstalledMiniApp,id=app_id)
    if not app:
        return JsonResponse({'error:':'App not Found!'},status=401)
    
    user_check=get_object_or_404(InstalledMiniApp,id=app_id,user=request.user)
    if not user_check.mini_app.name == "Share Mania":
        return HttpResponseBadRequest("Bad request or app is not installed")
    
    # FETCH SHARED FILES 
    shared_files = FileUploadMania.objects.filter(organization=organization,uploaded_by=request.user)
    
    context = {
        'organization':organization,
        'app':app,
        'shared_files':shared_files,
    }
    return render(request,'mini_apps/gui/share_mania.html',context)



# SHARE THE FILE 

@csrf_exempt
@check_org_membership
def upload_file(request, org_id):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        file_name = request.POST.get("file_name")
        expires_in_days = int(request.POST.get("expires_in_days", 7))  # Default 7 days

        organization = get_object_or_404(Organization, id=org_id)
        uploaded_by = request.user

        file_upload = FileUploadMania.objects.create(
            organization=organization,
            uploaded_by=uploaded_by,
            file=file,
            file_name=file_name,
            expires_in_days=expires_in_days,
        )

        # ✅ Use unique_link directly
        file_link = file_upload.unique_link  # Make sure this contains the full URL

        return JsonResponse({"success": True, "file_id": file_upload.id, "file_link": file_link})
    
    return JsonResponse({"success": False, "error": "Invalid request"})


# fetch team and send the mail

@check_org_membership
@csrf_exempt
def fetch_members_and_send_email(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)

    if request.method == "GET":
        # ✅ Handle GET request: Fetch organization members
        # ✅ Handle GET request: Fetch organization members
      members = Profile.objects.filter(organization=organization).values(
         "id", "full_name", "user"
        )

     # ✅ Manually add full profile picture URL
      for member in members:
        profile = Profile.objects.get(id=member["id"])  # Get full Profile object
        member["profile_picture"] = (
          settings.MEDIA_URL + str(profile.profile_picture)
        if profile.profile_picture
        else settings.STATIC_URL + "default-profile.png"
     )

        print("✅ MEMBERS FOUND:", members)
      return JsonResponse({"members": list(members)}, status=200)
    elif request.method == "POST":
        # ✅ Handle POST request: Send file link
        try:
            data = json.loads(request.body)
            file_id = data.get("file_id")
            selected_users = data.get("selected_users", [])

            print("SELECTED USERS:",selected_users)

            if not file_id:
                return JsonResponse({"success": False, "error": "Missing file_id"}, status=400)

            file_upload = get_object_or_404(FileUploadMania, id=file_id)
            # file_link = file_upload.unique_link  # ✅ Directly use stored URL
            # file_link = request.build_absolute_uri(file_upload.unique_link)  # ✅ Converts to full URL
            file_link = request.build_absolute_uri(f"/apps/download-file-preview/{file_upload.unique_link}/") 



            if not selected_users:
                return JsonResponse({"success": False, "error": "No users selected"}, status=400)
            


            # ✅ Sending emails to selected users
            for user_id in selected_users:
                user = get_object_or_404(User, id=user_id)
                file_upload.shared_with.add(user)
                file_upload.save()

                send_mail(
                    subject="Shared File Access",
                    message=f"Hello {user.username},\n\nA file has been shared with you. Access it here: {file_link}\n\nBest,\nCalendar Plus Team",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )

            return JsonResponse({"success": True, "message": "File link sent successfully!"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    # ❌ Invalid request method
    return JsonResponse({"success": False, "error": "Method Not Allowed"}, status=405)




# DOWNLOAD THE FILE
def file_details_view(request, unique_link):
    file_upload = get_object_or_404(FileUploadMania, unique_link=unique_link)

    organization=file_upload.organization
    print("file organization:",organization.name)

    profile=get_object_or_404(Profile,organization=organization,user=request.user)
    print("User organization:",profile.organization.name)
    if not profile:
        return HttpResponseBadRequest("You are not authorized to view this file")

    # Check if the file is expired
    if file_upload.is_expired():
        return render(request, "files/file_expired.html", {"file": file_upload})

    return render(request, "mini_apps/files/file_details.html", {"file": file_upload})


# DOWNLOAD THE FILE 
def download_file(request, unique_link):
    file_upload = get_object_or_404(FileUploadMania, unique_link=unique_link)

    if file_upload.is_expired():
        raise Http404("File has expired.")
    
    file_upload.downloaded_by.add(request.user)
    file_upload.save()

    response = FileResponse(file_upload.file.open("rb"), as_attachment=True, filename=file_upload.file_name)
    return response


# FETCH FILE DETAILS 
@login_required
@csrf_exempt
def fetch_file_details(request, unique_link):
    file = get_object_or_404(FileUploadMania, unique_link=unique_link)
    
    data = {
        "file_name": file.file_name,
        "file_size": f"{file.file_size / (1024 * 1024):.2f} MB",
        "uploaded_by": file.uploaded_by.username,
        "shared_with": ", ".join([user.username for user in file.shared_with.all()]) or "No one",
        "downloaded_by": ", ".join([user.username for user in file.downloaded_by.all()]) or "Not downloaded yet",
        "expires_at": file.expires_at.strftime("%Y-%m-%d %H:%M:%S"),
        "file_url": file.file.url,
        "is_expired": file.is_expired(),
    }
    print("DATA:",data)
    return JsonResponse(data)


# DELETE THE FILE 
@check_org_membership
def delete_file_upload(request,org_id,file_id,app_id):
    organization = get_object_or_404(Organization, id=org_id)
    file = get_object_or_404(FileUploadMania,id=file_id,organization=organization,uploaded_by=request.user)
    app=get_object_or_404(InstalledMiniApp,id=app_id)
    if not app:
        return HttpResponseBadRequest("App Not Found!")
    
    if not file:
        return HttpResponseBadRequest("Bad Request! you doesnt own this file!")
    file.delete()
    return redirect('share_mania_app',org_id=organization.id,app_id=app.id)

# SHARE-MANIA APP - COMPLETED --------------------------------------------------------------------------------------------




# ------------------------------------------------------------------------------------------------------------------------------
# APPS (TASK MANAGER - KANBAN BOARD)
# (CLI APPS)
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
    organization = get_object_or_404(Organization, id=org_id)
    # check access
    if not Profile.objects.filter(user=request.user, organization=organization).exists():
        return JsonResponse({'error:':'Unauthorized access'},status=400)

    
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
    # check access
    organization = get_object_or_404(Organization, id=org_id)
    if not Profile.objects.filter(user=request.user, organization=organization).exists():
        return JsonResponse({'error:':'Unauthorized access'},status=400)


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
            
            

            meeting = MeetingOrganization.objects.get(id=meeting_id, organization_id=org_id)
            organization = Organization.objects.get(id=org_id)
            user = User.objects.get(id=user_id)
            # check access
            if not Profile.objects.filter(user=request.user, organization=organization).exists():
                return JsonResponse({'error:':'Unauthorized access'},status=400)


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

# GET MEETING NOTES
def get_meeting_notes(request, meeting_id):
    if request.method == "GET":
        notes = MeetingNotes.objects.filter(meeting_id=meeting_id).values("id", "content", "created_at")
        return JsonResponse({"notes": list(notes)}, safe=False)

    return JsonResponse({"error": "Invalid request method."}, status=400)


# DELETE MEETING NOTES
def delete_meeting_note(request, note_id):
    if request.method == "POST":
        note = get_object_or_404(MeetingNotes, id=note_id)
        note.delete()
        return JsonResponse({"message": "Note deleted successfully!"})

    return JsonResponse({"error": "Invalid request method."}, status=400)

# ------------------------------------------------------------------------------------------------------------------------------------

# BOOKMARK MANAGER /manage-bookmarks
@check_org_membership
@login_required
def fetch_bookmarks(request, org_id):
    """Fetch all bookmarks for the given organization."""
    organization = get_object_or_404(Organization, id=org_id)
    bookmarks = Bookmark.objects.filter(organization=organization, created_by=request.user)
    if not Profile.objects.filter(user=request.user, organization=organization).exists():
        return JsonResponse({'error:':'Unauthorized access'},status=400)

    
    data = [
        {
            "id": bookmark.id,
            "title": bookmark.title,
            "url": bookmark.url,
            "description": bookmark.description,
            "category": bookmark.category,
            "app_logo": bookmark.app_logo.url if bookmark.app_logo else None,
        }
        for bookmark in bookmarks
    ]
    return JsonResponse({"bookmarks": data})


@check_org_membership
@csrf_exempt
@login_required
def delete_bookmark(request, org_id, bookmark_id):
    """Delete a bookmark only if it belongs to the correct organization."""
    organization = get_object_or_404(Organization, id=org_id)
    if not Profile.objects.filter(user=request.user, organization=organization).exists():
        return JsonResponse({'error:':'Unauthorized access'},status=400)

    bookmark = get_object_or_404(Bookmark, id=bookmark_id, organization=organization, created_by=request.user)
    
    bookmark.delete()
    return JsonResponse({"message": "Bookmark deleted successfully!"})

@check_org_membership
@csrf_exempt
@login_required
def add_bookmark(request, org_id):
    """Add a new bookmark under the specified organization."""
    organization = get_object_or_404(Organization, id=org_id)
    if not Profile.objects.filter(user=request.user, organization=organization).exists():
        return JsonResponse({'error:':'Unauthorized access'},status=400)


    if request.method == "POST":
        title = request.POST.get("title")
        url = request.POST.get("url")
        description = request.POST.get("description", "")
        category = request.POST.get("category", "")
        app_logo = request.FILES.get("app_logo")

        if not title or not url:
            return JsonResponse({"error": "Title and URL are required."}, status=400)

        Bookmark.objects.create(
            organization=organization,
            created_by=request.user,
            title=title,
            url=url,
            description=description,
            category=category,
            app_logo=app_logo,
        )
        return JsonResponse({"message": "Bookmark added successfully!"})
    
    return JsonResponse({"error": "Invalid request"}, status=400)

# --------------------------------------------------------------------------------------------------------------------------------------------------

# SHARE - MANIA -- completed
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------


# AJAX SET-UP PREVIEW UNINSTALL APPS
@login_required
def fetch_installed_apps(request, org_id):
    """Fetch installed apps for a user in the given organization."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    organization = get_object_or_404(Organization, id=org_id)
    if not Profile.objects.filter(user=request.user, organization=organization).exists():
        return JsonResponse({'error:':'Unauthorized access'},status=400)

    
    # Fetch installed apps for the user in the given organization
    installed_apps = InstalledMiniApp.objects.filter(user=request.user, organization=organization).select_related("mini_app")

    # Prepare JSON response
    data = [
        {
            "id":app.id,
            "name": app.mini_app.name,
            "icon": app.mini_app.icon.url if app.mini_app.icon else None,
            "version": app.mini_app.version,
        }
        for app in installed_apps
    ]

    return JsonResponse({"installed_apps": data})

# Uninstall the app
@login_required
def uninstall_app(request, org_id, app_id):
    """
    View to uninstall an app for a user within an organization.
    """
    user = request.user
    organization = get_object_or_404(Organization, id=org_id)
    if not Profile.objects.filter(user=request.user, organization=organization).exists():
        return JsonResponse({'error:':'Unauthorized access'},status=400)


    # Check if the app is installed
    installed_app = InstalledMiniApp.objects.filter(
        user=user, 
        organization_id=org_id, 
        id=app_id
    ).first()

    if not installed_app:
        return JsonResponse({"error": "App is not installed or already removed."}, status=400)

    # Delete the installation record
    installed_app.delete()

    return JsonResponse({"success": True, "message": "App uninstalled successfully!"})


# fetch details during uninstallation
@login_required
def fetch_app_details(request,org_id,app_id):
    """
    Fetch the details of a MiniApp before installation using filter().
    """
    organization = get_object_or_404(Organization, id=org_id)
    app = InstalledMiniApp.objects.filter(id=app_id).first()

    if not Profile.objects.filter(user=request.user, organization=organization).exists():
        return JsonResponse({'error:':'Unauthorized access'},status=400)

    if not app:
        return JsonResponse({"error": "App not found."}, status=404)

    app_data = {
        "name": app.mini_app.name,
        "description": app.mini_app.description,
        "icon": app.mini_app.icon.url if app.mini_app.icon else None,
        "category": app.mini_app.get_category_display(),
        "developer": app.mini_app.developer,
        "version": app.mini_app.version,
        "size": app.mini_app.size,
        "is_premium": app.mini_app.is_premium,
        "install_count": app.mini_app.install_count,
        "requirements": app.mini_app.requirements,
        "ratings": app.mini_app.ratings,
     
    }

    return JsonResponse({"success": True, "app_details": app_data})