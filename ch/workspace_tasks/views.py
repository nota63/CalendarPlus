from django.shortcuts import render,redirect,get_object_or_404
from accounts.models import Organization
from .models import TaskOrganization
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
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