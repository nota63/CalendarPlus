from group_tasks.models import Task, TaskTimeTracking,CalPoints
from accounts.models import Organization , Profile
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q,Sum
from django.db import models 
from django.shortcuts import get_object_or_404
import re 

# 1)Fetch time traced
def task_time_tracking_summary(request, org_id):
    user = request.user

    # check access
    if not Profile.objects.filter(user=user,organization_id=org_id).exists():
        return JsonResponse({'error:':'You are not authorized to view this!'}, status=400)

    # Fetch only tracked tasks assigned to the user
    time_logs = TaskTimeTracking.objects.filter(
        organization_id=org_id,
        task__assigned_to=user
    ).select_related('task')

    response_data = []
    for log in time_logs:
        response_data.append({
            'task_title': log.task.title,
            'start_time': log.start_time.strftime('%Y-%m-%d %H:%M'),
            'end_time': log.end_time.strftime('%Y-%m-%d %H:%M') if log.end_time else 'In Progress',
            'time_spent': float(log.time_spent),
            'duration': round(log.get_duration(), 2)  # In hours
        })

    return JsonResponse({'success': True, 'data': response_data})


# Widget 2) High priority tasks widget ---------------------------------------------------------------------------------------------------------------

@login_required
def high_priority_tasks_widget(request, org_id):

    # check access 
    if not Profile.objects.filter(user=request.user,organization_id=org_id).exists():
        return JsonResponse({'error:':'Unauthorized Access'}, status=400)
    
    tasks = Task.objects.filter(
        organization_id=org_id,
        assigned_to=request.user,
        priority__in=['high', 'urgent'],
        status__in=['pending', 'in_progress', 'overdue', 'pending_approval', 'need_changes']
    ).select_related('group')

    task_data = [
        {
            "id": task.id,
            "title": task.title,
            "group_name": task.group.name,
            'progress':task.progress,
            "status": task.status.replace("_", " ").title(),
            "deadline": task.deadline.strftime('%Y-%m-%d %H:%M')
        }
        for task in tasks
    ]

    return JsonResponse({"tasks": task_data})


# //  Widget 3) Total Calpoints Earned --------------------------------------------------------------------------------------------------------

@login_required
def get_calpoints_balance_view(request, org_id):
    user = request.user
    try:
        profile = Profile.objects.get(user=user, organization_id=org_id)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found for this organization.'}, status=404)

    calpoints = CalPoints.objects.filter(user=user, organization_id=org_id)
    total_points = calpoints.aggregate(total=Sum('points'))['total'] or 0

    return JsonResponse({
        'total_points': total_points,
        'username': profile.full_name or user.username,
        'profile_pic': profile.profile_picture.url if profile.profile_picture else '',
        'organization_name': profile.organization.name
    })

# Fetch calpoints history
@login_required
def fetch_calpoints_history(request, org_id):
    """
    Fetch the CalPoints history for a user, given an organization ID.
    Returns the points earned and when they were awarded.
    """
    # Fetch user's profile and organization info
    profile=Profile.objects.filter(user=request.user,organization_id=org_id).first()
    user_profile = profile.profile_picture.url if profile.profile_picture else None
    organization = get_object_or_404(Organization,id=org_id)

    # check the access 
    if not profile:
        return JsonResponse({'error:':'You are not authorized!'}, status=400)

    # Check if the user belongs to the given organization
    if organization.id != org_id:
        return JsonResponse({"error": "Unauthorized access"}, status=403)

    # Fetch the CalPoints data for the user and organization
    calpoints_history = CalPoints.objects.filter(
        user=request.user, organization=organization
    ).values('created_at', 'points')

    # Create a list to return the points history with the formatted date
    history_data = [
        {
            'created_at': point['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
            'points': point['points']
        }
        for point in calpoints_history
    ]

    # Return the data as a JsonResponse
    return JsonResponse({
        "history": history_data,
        "total_points": calpoints_history.aggregate(total_points=models.Sum('points'))['total_points'] or 0
    })


# // widget 4) Embed a Google Doc -----------------------------------------------------------------------------------------------

# Function to validate if the URL is a Google Doc URL
# Function to validate if the URL is a Google Doc URL
# Set up a logger
import logging
logger = logging.getLogger(__name__)
def embed_google_doc(request):
    if request.method == 'POST':
        doc_url = request.POST.get('doc_url')

        if not doc_url:
            return JsonResponse({'error': 'No URL provided'}, status=400)

        logger.debug(f"Received Google Doc URL: {doc_url}")

        # Bypass validation and directly extract document ID
        try:
            # Extract the document ID from the URL (this assumes the URL follows the correct format)
            doc_id = doc_url.split('/d/')[1].split('/')[0]
            # Change the URL to allow editing
            edit_url = f'https://docs.google.com/document/d/{doc_id}/edit'
            logger.debug(f"Generated edit URL: {edit_url}")
            return JsonResponse({'embed_url': edit_url})
        except Exception as e:
            logger.error(f"Error extracting doc_id: {str(e)}")
            return JsonResponse({'error': 'Failed to extract document ID'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# // widget 5) Google Sheets ----------------------------------------------------------------------------------------------------------------------------
def is_google_sheet_url(url):
    pattern = r'https:\/\/docs\.google\.com\/spreadsheets\/d\/[a-zA-Z0-9-_]+'
    return re.match(pattern, url) is not None

def embed_google_sheet(request):
    if request.method == 'POST':
        sheet_url = request.POST.get('sheet_url')

        if not sheet_url:
            return JsonResponse({'error': 'No URL provided'}, status=400)

        if is_google_sheet_url(sheet_url):
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            embed_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/edit?usp=sharing'

            return JsonResponse({'embed_url': embed_url})

        return JsonResponse({'error': 'Invalid Google Sheets URL'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
