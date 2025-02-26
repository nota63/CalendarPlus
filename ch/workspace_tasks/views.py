from django.shortcuts import render,redirect,get_object_or_404
from accounts.models import Organization
from .models import TaskOrganization
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.contrib.auth.models import User
from django.http import JsonResponse

# Workspace Tasks


# Create a task



@method_decorator(csrf_exempt, name='dispatch')  # For handling AJAX requests
def create_task(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Extracting required fields
            org_id = data.get("org_id")
            title = data.get("title")
            description = data.get("description", "")
            assigned_to_id = data.get("assigned_to")
            priority = data.get("priority", "medium")
            due_date = data.get("due_date", None)
            depends_on_id = data.get("depends_on", None)

            # Validate required fields
            if not org_id or not title or not assigned_to_id:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Get the organization
            organization = get_object_or_404(Organization, id=org_id)

            # Get the assigned user
            assigned_to = get_object_or_404(User, id=assigned_to_id)

            # Handle task dependency
            depends_on = None
            if depends_on_id:
                depends_on = TaskOrganization.objects.filter(id=depends_on_id).first()

            # Create the task
            task = TaskOrganization.objects.create(
                title=title,
                description=description,
                assigned_to=assigned_to,
                organization=organization,
                priority=priority,
                due_date=due_date,
                depends_on=depends_on
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



