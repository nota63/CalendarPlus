from django.http import JsonResponse,Http404
from django.contrib.auth.decorators import login_required
from .models import BookMarksWidget,RecentActivity
from accounts.models import Organization, Profile
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.timezone import now
import json
from django.views import View
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseBadRequest
from group_tasks.models import CommunicateTask
# Fetch bookmarks

class UserBookmarksView(View):
    def get(self, request, org_id):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required.'}, status=401)

        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            raise Http404("Organization not found.")

        try:
            widget = BookMarksWidget.objects.get(organization=organization, created_by=request.user)
        except BookMarksWidget.DoesNotExist:
            return JsonResponse({'data': [], 'message': 'No bookmarks found.'}, status=200)

        return JsonResponse({'data': widget.data}, status=200)


# Create new bookmark
@csrf_exempt
@login_required
@require_POST
def add_bookmark(request, org_id):
    try:
        data = json.loads(request.body)
        title = data.get('title')
        url = data.get('url')

        if not title or not url:
            return JsonResponse({'error': 'Both title and URL are required.'}, status=400)

        organization = Organization.objects.get(id=org_id)

        # Get or create the widget for this user-org pair
        widget, created = BookMarksWidget.objects.get_or_create(
            organization=organization,
            created_by=request.user,
            defaults={'data': []}
        )

        # Create a new bookmark object
        new_bookmark = {
            "title": title,
            "url": url,
            "added_at": timezone.now().isoformat()
        }

        # Append to data list
        widget.data.append(new_bookmark)
        widget.save()

        return JsonResponse({'message': 'Bookmark added successfully!'})

    except Organization.DoesNotExist:
        return JsonResponse({'error': 'Organization not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Delete the bookmarks
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def delete_bookmark(request, org_id, bookmark_id):
    try:
        widget = BookMarksWidget.objects.get(organization_id=org_id, created_by=request.user)
        bookmark_id = int(bookmark_id)

        if bookmark_id < 0 or bookmark_id >= len(widget.data):
            return HttpResponseBadRequest("Invalid bookmark ID.")

        # Remove the bookmark from the list
        widget.data.pop(bookmark_id)
        widget.save()

        return JsonResponse({'success': True, 'message': 'Bookmark deleted successfully'})
    except BookMarksWidget.DoesNotExist:
        return HttpResponseBadRequest("Bookmarks widget not found.")
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    

# // Widget 2 ) - Resources Widget ----------------------------------------------------------------------------------------------------

# // fetch and display the resources uploaded by the user accross the workspace

@login_required
def user_resources_view(request, org_id):
    user = request.user

    # Fetch task communication files by the user in this organization
    task_files = CommunicateTask.objects.filter(
        organization_id=org_id,
        sender=user,
        files__isnull=False
    ).exclude(files='')

    task_files_data = [
        {
            "file_url": task_file.files.url,
            "uploaded_at": task_file.created_at.strftime('%Y-%m-%d %H:%M'),
            "file_name": task_file.files.name.split('/')[-1],
            "type": "task_file"
        }
        for task_file in task_files
    ]

    # Fetch profile picture if uploaded
    try:
        profile_pic = Profile.objects.get(user=user, organization_id=org_id).profile_picture
        if profile_pic:
            profile_data = [{
                "file_url": profile_pic.url,
                "uploaded_at": None,
                "file_name": profile_pic.name.split('/')[-1],
                "type": "profile_picture"
            }]
        else:
            profile_data = []
    except Profile.DoesNotExist:
        profile_data = []

    return JsonResponse({
        "status": "success",
        "data": task_files_data + profile_data
    })


  
# // Widget 3 ) - Recent activities widget ----------------------------------------------------------------------------------------------------

# Fetch recent activities
@login_required
def fetch_recent_activity_methods(request, org_id):
    """
    Fetch recent activity entries with ID and method for the logged-in user.
    Note: org_id is accepted but not used for filtering currently.
    """
    user = request.user

    recent_activities = RecentActivity.objects.filter(
        user=user
    ).order_by('-timestamp')[:50]

    data = [
        {
            "id": activity.id,
            "method": activity.method
        }
        for activity in recent_activities
    ]

    return JsonResponse({"activities": data}, status=200)