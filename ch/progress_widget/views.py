from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from group_tasks.models import Task  


# Fetch tasks progress along with group names
@login_required
def user_task_progress_widget(request, org_id):
    user = request.user

    tasks = Task.objects.filter(
        organization_id=org_id,
        assigned_to=user
    ).select_related("group").values(
        "title",
        "progress",
        "group__name"
    )

    return JsonResponse({
        "tasks": list(tasks)
    }, safe=False)
