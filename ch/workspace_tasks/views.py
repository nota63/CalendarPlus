from django.shortcuts import render,redirect,get_object_or_404
from accounts.models import Organization,Profile
from .models import TaskOrganization
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
# Workspace Tasks


# Create a task
@csrf_protect  # ✅ We now use CSRF protection
def create_task(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            org_id = data.get("org_id")
            title = data.get("title")
            description = data.get("description", "")
            priority = data.get("priority", "medium")
            due_date = data.get("due_date", None)
            depends_on_id = data.get("depends_on", None)

            if not org_id or not title:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            organization = get_object_or_404(Organization, id=org_id)

            depends_on = None
            if depends_on_id:
                depends_on = TaskOrganization.objects.filter(id=depends_on_id).first()

            task = TaskOrganization.objects.create(
                title=title,
                description=description,
                organization=organization,
                priority=priority,
                due_date=due_date,
                depends_on=depends_on,
                creator=request.user
            )

            return JsonResponse({
                "message": "Task created successfully!",
                "task_id": task.id,
                "title": task.title,
                "priority": task.priority,
                "status": task.status
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)




# Manage Tasks
def organization_tasks(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)
    tasks = TaskOrganization.objects.filter(organization=organization,creator=request.user).values("id", "title", "status")

    return JsonResponse({"tasks": list(tasks)}, safe=False)




# update task status
@csrf_exempt
def update_task_status(request, task_id):
    if request.method == "POST":
        data = json.loads(request.body)
        task = TaskOrganization.objects.get(id=task_id)
        task.status = data["status"]
        task.save()
        return JsonResponse({"message": "Task updated successfully!"})



# Edit Profile
import logging
logger = logging.getLogger(__name__)
@login_required
@csrf_protect  
def edit_profile(request, org_id):
    """Fetch & update user's profile (profile picture & full name) via AJAX."""
    
    organization = get_object_or_404(Organization, id=org_id)
    user = request.user
    profile = Profile.objects.filter(user=user, organization=organization).first()

    if not profile:
        profile = Profile.objects.create(user=user, organization=organization, full_name=user.get_full_name())

    if request.method == "GET":
        logger.info(f"Fetching profile for user {user} in org {org_id}")
        return JsonResponse({
            "success": True,
            "profile": {
                "full_name": profile.full_name,
                "profile_picture": profile.profile_picture.url if profile.profile_picture else None,
            }
        })

    elif request.method == "POST":
        try:
            full_name = request.POST.get("full_name", "").strip()
            if full_name:
                profile.full_name = full_name
                profile.save(update_fields=["full_name"])

            # Save the profile picture if it's uploaded
            if "profile_picture" in request.FILES:
                profile.profile_picture = request.FILES["profile_picture"]
                profile.save(update_fields=["profile_picture"])  # Ensure it's explicitly saved

            logger.info(f"Profile updated for user {user}: Full Name: {profile.full_name}, Picture Updated: {'Yes' if 'profile_picture' in request.FILES else 'No'}")

            return JsonResponse({
                "success": True,
                "message": "Profile updated successfully!",
                "full_name": profile.full_name,
                "profile_picture": profile.profile_picture.url if profile.profile_picture else None
            })

        except Exception as e:
            logger.error(f"Error updating profile for user {user}: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})
