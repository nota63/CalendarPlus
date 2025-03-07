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
    print("➡️ Received request for scheduling a meeting...")

    if request.method != "POST":
        print("❌ Invalid request method:", request.method)
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        # Parse JSON request data
        print("📩 Reading JSON data...")
        data = json.loads(request.body)
        print("✅ Parsed JSON data:", data)

        emails = data.get("emails", [])
        time = data.get("time")
        recurrence = data.get("recurrence")
        custom_date = data.get("custom_date")
        skip_if_busy = data.get("skip_if_busy", False)
        meeting_title = data.get("meeting_title")

        print(f"📌 Extracted fields: emails={emails}, time={time}, recurrence={recurrence}, "
              f"custom_date={custom_date}, skip_if_busy={skip_if_busy}, meeting_title={meeting_title}")

        # Validate required fields
        if not emails or not time or not recurrence or not meeting_title:
            print("❌ Missing required fields!")
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Validate organization
        print(f"🏢 Fetching organization (ID: {org_id})...")
        organization = get_object_or_404(Organization, id=org_id)
        creator = request.user  # Assuming user is authenticated
        print(f"✅ Organization found: {organization.name} | Creator: {creator}")

        # Match emails with users in the organization
        print("🔍 Finding users in the organization for provided emails...")
        users = User.objects.filter(email__in=emails, profile__organization=organization)
        print(f"✅ Found {users.count()} valid users.")

        if not users.exists():
            print("❌ No valid users found!")
            return JsonResponse({"error": "No valid users found for the provided emails"}, status=400)

        # Validate time format (HH:MM)
        try:
            print(f"⏰ Validating time format: {time}...")
            meeting_time = datetime.strptime(time, "%H:%M").time()
            print(f"✅ Valid time: {meeting_time}")
        except ValueError:
            print("❌ Invalid time format!")
            return JsonResponse({"error": "Invalid time format. Use HH:MM."}, status=400)

        # Validate custom date format (if recurrence is 'custom')
        if recurrence == "custom":
            if not custom_date:
                print("❌ Custom date required for 'custom' recurrence!")
                return JsonResponse({"error": "Custom date is required when recurrence is 'custom'"}, status=400)
            try:
                print(f"📅 Validating custom date: {custom_date}...")
                custom_date = datetime.strptime(custom_date, "%Y-%m-%d").date()
                print(f"✅ Valid custom date: {custom_date}")
            except ValueError:
                print("❌ Invalid date format!")
                return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
        else:
            print("🔄 Recurrence is NOT 'custom', skipping custom date validation.")
            custom_date = None  # Reset if not custom

        # Create the AutoSchedule entry
        print("📝 Creating AutoSchedule entry...")
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
        print(f"✅ AutoSchedule entry created: ID={auto_schedule.id}")

        auto_schedule.scheduled_with.set(users)  # Associate matched users
        auto_schedule.save()
        print(f"✅ Associated {users.count()} users with the meeting.")

        return JsonResponse({
            "success": "Meeting scheduled successfully!",
            "meeting_id": auto_schedule.id
        }, status=201)

    except ValidationError as e:
        print("❌ Validation error:", str(e))
        return JsonResponse({"error": str(e)}, status=400)

    except json.JSONDecodeError:
        print("❌ JSON Decode Error: Invalid JSON format!")
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    except Exception as e:
        print("❌ Unexpected error:", str(e))
        return JsonResponse({"error": "An unexpected error occurred", "details": str(e)}, status=500)