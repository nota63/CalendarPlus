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
    
    # check already scheduled meets
    scheduled_meets=AutoSchedule.objects.filter(organization=organization,creator=request.user)
    
    context = {
        'organization':organization,
        'app':app,
        'scheduled_meets':scheduled_meets,
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
        remind_check=data.get('remind_check',False)
        retry_if_failed=data.get('retry_check',False)

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

        # Match emails with users in the organization via Profile model
        print("🔍 Finding users in the organization for provided emails...")
        profiles = Profile.objects.filter(user__email__in=emails, organization=organization)

        if not profiles.exists():
            print("❌ No valid profiles found!")
            return JsonResponse({"error": "No valid users found for the provided emails"}, status=400)

        users = [profile.user for profile in profiles]  # Extract user instances from profiles
        print(f"✅ Found {len(users)} valid users.")

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
            meeting_title=meeting_title,
            organization=organization,
            creator=creator,
            time=meeting_time,
            recurrence=recurrence,
            custom_date=custom_date,
            skip_if_busy=skip_if_busy,
            status=AutoSchedule.StatusChoices.PENDING,
            conflict_detected=False,
            remind_check=remind_check,
            retry_if_failed=retry_if_failed,
        )
        print(f"✅ AutoSchedule entry created: ID={auto_schedule.id}")

        auto_schedule.scheduled_with.set(users)  # Associate matched users
        auto_schedule.save()
        print(f"✅ Associated {len(users)} users with the meeting.")

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


# delete the entry
@check_org_membership
@login_required
def delete_automation(request,org_id,automation_id,app_id):
    organization = get_object_or_404(Organization, id=org_id)
    automation=get_object_or_404(AutoSchedule,id=automation_id,organization=organization)
    app=get_object_or_404(InstalledMiniApp,id=app_id)
    if not app:
        return JsonResponse({'error:':'App not found!'},status=400)
    automation.delete()
    return redirect('automate_scheduling',org_id=organization.id,app_id=app.id)

# CONFIGURE THE AUTOMATION
@check_org_membership
def get_automation(request, org_id, automation_id):
    """Fetches automation schedule details."""
    schedule = get_object_or_404(AutoSchedule, id=automation_id, organization_id=org_id)

    data = {
        "meeting_title": schedule.meeting_title,
        "time": schedule.time.strftime("%H:%M"),
        "recurrence": schedule.recurrence,
        "custom_date": schedule.custom_date.strftime("%Y-%m-%d") if schedule.custom_date else "",
        "skip_if_busy": schedule.skip_if_busy,
        "remind_check": schedule.remind_check,
        "retry_if_failed": schedule.retry_if_failed,
    }
    return JsonResponse(data)

@check_org_membership
def update_automation(request, org_id, automation_id):
    """Updates the automation schedule."""
    if request.method == "POST":
        print("🔹 Received POST request for updating automation.")  # Debugging

        try:
            schedule = get_object_or_404(AutoSchedule, id=automation_id, organization_id=org_id)
            print(f"✅ Found Schedule: {schedule}")

            # Debugging: Print received data
            print("🔹 Request POST Data:", request.POST)

            meeting_title = request.POST.get("meeting_title", "").strip()
            time = request.POST.get("time")
            recurrence = request.POST.get("recurrence")
            custom_date = request.POST.get("custom_date") or None
            skip_if_busy = request.POST.get("skip_if_busy") == "on"
            remind_check = request.POST.get("remind_check") == "on"
            retry_if_failed = request.POST.get("retry_if_failed") == "on"

            # Debugging: Print extracted values
            print(f"🔹 Extracted Values: \n"
                  f"   - Meeting Title: {meeting_title}\n"
                  f"   - Time: {time}\n"
                  f"   - Recurrence: {recurrence}\n"
                  f"   - Custom Date: {custom_date}\n"
                  f"   - Skip If Busy: {skip_if_busy}\n"
                  f"   - Remind Check: {remind_check}\n"
                  f"   - Retry If Failed: {retry_if_failed}")

            # Ensure meeting_title is not empty
            if not meeting_title:
                print("❌ Error: Meeting title is missing!")
                return JsonResponse({"success": False, "error": "Meeting title is required"}, status=400)

            # Update only if valid
            AutoSchedule.objects.filter(id=automation_id, organization_id=org_id).update(
                meeting_title=meeting_title,
                time=time,
                recurrence=recurrence,
                custom_date=custom_date,
                skip_if_busy=skip_if_busy,
                remind_check=remind_check,
                retry_if_failed=retry_if_failed,
            )

            print("✅ Successfully updated schedule!")
            return JsonResponse({"success": True})

        except Exception as e:
            print(f"❌ Exception Occurred: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    print("❌ Error: Request method is not POST!")
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)