
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import DashboardWidget
from accounts.models import Organization 
from django.views.decorators.http import require_POST


# Save the widget 
@csrf_exempt
@login_required
@require_POST
def save_dashboard_widget(request):
    try:
        print("🧠 Incoming POST to save widget")

        data = json.loads(request.body)
        org_id = data.get("org_id")
        widget_type = data.get("widget_type")

        print(f"📦 Parsed Data -> org_id: {org_id}, widget_type: {widget_type}")

        if not org_id or not widget_type:
            print("❌ Missing org_id or widget_type in request.")
            return JsonResponse({"error": "Missing required data"}, status=400)

        try:
            org = Organization.objects.get(id=org_id)
            print(f"✅ Found organization: {org}")
        except Organization.DoesNotExist:
            print(f"❌ Organization not found with ID: {org_id}")
            return JsonResponse({"error": "Organization not found"}, status=404)

        widget_exists = DashboardWidget.objects.filter(
            organization=org,
            user=request.user,
            widget_type=widget_type
        ).exists()

        if widget_exists:
            print("⚠️ Widget already exists for this user and org.")
            return JsonResponse({"message": "Widget already added"}, status=200)

        position = DashboardWidget.objects.filter(user=request.user, organization=org).count()
        new_widget = DashboardWidget.objects.create(
            organization=org,
            user=request.user,
            widget_type=widget_type,
            position=position + 1
        )

        print(f"✅ Widget created successfully: {new_widget}")
        return JsonResponse({"message": "Widget added successfully"}, status=201)

    except json.JSONDecodeError:
        print("❌ Failed to decode JSON")
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        print("💥 Unexpected error occurred:", str(e))
        return JsonResponse({"error": str(e)}, status=500)