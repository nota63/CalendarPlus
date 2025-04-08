# views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import DashboardWidget
from accounts.models import Organization 



# Save the widget 
@method_decorator([csrf_exempt, login_required], name='dispatch')
class SaveDashboardWidgetView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            org_id = data.get("org_id")
            widget_type = data.get("widget_type")

            if not org_id or not widget_type:
                return JsonResponse({"error": "Missing data"}, status=400)

            org = Organization.objects.get(id=org_id)

            # Check if widget already exists
            widget_exists = DashboardWidget.objects.filter(
                organization=org,
                user=request.user,
                widget_type=widget_type
            ).exists()

            if widget_exists:
                return JsonResponse({"message": "Widget already added"}, status=200)

            # Create widget
            position = DashboardWidget.objects.filter(user=request.user, organization=org).count()
            DashboardWidget.objects.create(
                organization=org,
                user=request.user,
                widget_type=widget_type,
                position=position + 1  # Append at the end
            )

            return JsonResponse({"message": "Widget added successfully"}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
