from django.shortcuts import render,redirect,get_list_or_404,get_object_or_404
from .models import MiniApp,InstalledMiniApp
from accounts.models import Organization, Profile
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponseBadRequest

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
from organization_channels.models import Channel, Message,ActivityChannel,Link,ChannelAccess,ChannelEvents
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