from django.http import JsonResponse,Http404
from django.contrib.auth.decorators import login_required
from .models import BookMarksWidget
from accounts.models import Organization
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.timezone import now
import json
from django.views import View
from django.utils import timezone
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
