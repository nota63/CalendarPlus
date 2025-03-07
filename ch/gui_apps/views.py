from django.shortcuts import render,redirect,get_object_or_404
from app_marketplace.models import MiniApp,InstalledMiniApp
from accounts.models import Profile, Organization
from django.http import JsonResponse, HttpResponse, HttpRequest,HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from app_marketplace.check_org_membership import check_org_membership
from .models import AutoSchedule
from datetime import datetime
import json
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
# 1) AUTOMATE SCHEDULING ----------------------------------------------------------------------------------------------------------------------------------------

# SCHEDULE THE MEET 

@check_org_membership
@login_required
def automate_scheduling(request,org_id,app_id):
    organization = get_object_or_404(Organization,id=org_id)
    app=get_object_or_404(InstalledMiniApp,id=app_id,organization=organization)
    if not app:
        return JsonResponse({'error:':'App not Found!'},status=401)
    
    user_check=get_object_or_404(InstalledMiniApp,id=app_id,user=request.user)
    if not user_check.mini_app.name == "Automate Scheduling":
        return HttpResponseBadRequest("Bad request or app is not installed")
    
    context = {
        'organization':organization,
        'app':app,
    }
    
    return render(request,'gui_apps/automate_scheduling/automate_scheduling.html',context)


# SCHEDULE THE MEET 
@csrf_exempt
@check_org_membership
def schedule_meeting(request, org_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        # Parse JSON request data
        data = json.loads(request.body)
        emails = data.get("emails", [])
        time = data.get("time")
        recurrence = data.get("recurrence")
        custom_date = data.get("custom_date")
        skip_if_busy = data.get("skip_if_busy", False)
        meeting_title = data.get("meeting_title")

        # Validate required fields
        if not emails or not time or not recurrence or not meeting_title:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Validate organization
        organization = get_object_or_404(Organization, id=org_id)
        creator = request.user  # Assuming user is authenticated

        # Match emails with users in the organization
        users = User.objects.filter(email__in=emails, profile__organization=organization)
        if not users.exists():
            return JsonResponse({"error": "No valid users found for the provided emails"}, status=400)

        # Validate time format (HH:MM)
        try:
            meeting_time = datetime.strptime(time, "%H:%M").time()
        except ValueError:
            return JsonResponse({"error": "Invalid time format. Use HH:MM."}, status=400)

        # Validate custom date format (if recurrence is 'custom')
        if recurrence == "custom":
            if not custom_date:
                return JsonResponse({"error": "Custom date is required when recurrence is 'custom'"}, status=400)
            try:
                custom_date = datetime.strptime(custom_date, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
        else:
            custom_date = None  # Reset if not custom

        # Create the AutoSchedule entry
        auto_schedule = AutoSchedule.objects.create(
            organization=organization,
            creator=creator,
            time=meeting_time,
            recurrence=recurrence,
            custom_date=custom_date,
            skip_if_busy=skip_if_busy,
            status=AutoSchedule.StatusChoices.PENDING,
            conflict_detected=False,
        )
        auto_schedule.scheduled_with.set(users)  # Associate matched users
        auto_schedule.save()

        return JsonResponse({
            "success": "Meeting scheduled successfully!",
            "meeting_id": auto_schedule.id
        }, status=201)

    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    except Exception as e:
        return JsonResponse({"error": "An unexpected error occurred", "details": str(e)}, status=500)