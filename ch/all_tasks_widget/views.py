from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from group_tasks.models import Task  
from accounts.models import Organization, Profile


# Widget 1) Number of tasks in progress 

@csrf_exempt
@login_required
def tasks_in_progress_count(request, org_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    # check access
    if not Profile.objects.filter(user=request.user, organization_id=org_id).exists():
        return JsonResponse({'error:':'Unauthorized access'}, status=400)
    

    try:
        user = request.user
        task_count = Task.objects.filter(
            organization_id=org_id,
            assigned_to=user,
            status='in_progress'
        ).count()

        return JsonResponse({'count': task_count})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
