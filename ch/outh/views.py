from django.shortcuts import render

# Create your views here.
from google_auth_oauthlib.flow import Flow
from django.conf import settings
from django.shortcuts import redirect
import os
from django.http import JsonResponse
from .models import GoogleAuth
from django.contrib.auth.decorators import login_required
import json
import csv
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.auth.exceptions import GoogleAuthError
from .models import GoogleAuth  # Assuming you have a GoogleAuth model
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from google.auth.transport.requests import Request


# Initiation template

def google(request):

    return render(request,'outh/login/initiate.html')



# TEMPORARILY ALLOW HTTP FOR DEVELOPMENT
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

def google_calendar_connect(request):
    """ Redirects user to Google OAuth consent page """
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/calendar.readonly","https://www.googleapis.com/auth/calendar.events",
                 "https://www.googleapis.com/auth/calendar"],
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    authorization_url, _ = flow.authorization_url(prompt="consent")

    return redirect(authorization_url)

# -----------------------------------------------------------------------------------



def google_calendar_callback(request):
    """Handles Google OAuth2 callback and stores credentials in the database."""

    try:
        user = request.user  # ✅ Get the authenticated user

        if not user.is_authenticated:
            return redirect('login')

        # 🔹 Create OAuth2 flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=["https://www.googleapis.com/auth/calendar.readonly","https://www.googleapis.com/auth/calendar",
             "https://www.googleapis.com/auth/calendar.events"],
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

        # 🔹 Exchange authorization code for tokens
        flow.fetch_token(authorization_response=request.build_absolute_uri())

        credentials = flow.credentials

        # ✅ Debug: Print credentials
        print("\n✅ [DEBUG] Credentials obtained:", credentials.to_json())

        # ✅ Ensure refresh token is stored (Google may not always send one)
        refresh_token = credentials.refresh_token
        if not refresh_token:
            # Try fetching the existing refresh token from DB
            existing_auth = GoogleAuth.objects.filter(user=user).first()
            if existing_auth and existing_auth.refresh_token:
                refresh_token = existing_auth.refresh_token

        # 🔹 Store credentials in the database
        google_auth, created = GoogleAuth.objects.update_or_create(
            user=user,
            defaults={
                "access_token": credentials.token,
                "refresh_token": refresh_token,  # Ensure refresh token is saved
                "scopes": credentials.scopes,
            }
        )

        print(f"\n✅ [SUCCESS] Google credentials saved for user: {user.username}")

        return JsonResponse({"message": "Google Calendar connected successfully!"})

    except GoogleAuthError as e:
        print("\n❌ [ERROR] Google OAuth2 Authentication Failed:", str(e))
        return JsonResponse({"error": "Google OAuth2 Authentication Failed"}, status=400)

    except Exception as e:
        print("\n❌ [ERROR] Unexpected Error:", str(e))
        return JsonResponse({"error": str(e)}, status=400)




# Calendar Connected successfully

@login_required
def get_google_events(request):
    """Fetch past & future Google Calendar events and return as JSON."""
    try:
        user = request.user
        creds_data = GoogleAuth.objects.filter(user=user).first()

        if not creds_data:
            return JsonResponse({'error': 'Google credentials not found'}, status=400)

        # ✅ Load credentials
        creds = Credentials(
            token=creds_data.access_token,
            refresh_token=creds_data.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=creds_data.scopes,
        )

        # ✅ Refresh token if expired
        if creds.expired and creds.refresh_token:
            print("\n🔄 [INFO] Token expired, refreshing...")

            creds.refresh(Request())

            # ✅ Save new access token
            creds_data.access_token = creds.token
            creds_data.save()

            print(f"\n✅ [SUCCESS] New Access Token: {creds.token}")

        # ✅ Connect to Google Calendar API
        service = build("calendar", "v3", credentials=creds)

        # ✅ Fetch primary calendar ID
        calendar_id = "primary"  # Change if needed

        # ✅ Define time range (Past 30 days → Future 6 months)
        time_min = (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"
        time_max = (datetime.utcnow() + timedelta(days=180)).isoformat() + "Z"

        print(f"\n📅 [DEBUG] Fetching events from {time_min} to {time_max}")

        # ✅ Fetch events
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=50,  # Fetch up to 50 events
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        # ✅ Extract event details
        events = [
            {
                "id": event["id"],
                "title": event.get("summary", "No Title"),
                "start": event["start"].get("dateTime", event["start"].get("date")),
                "end": event["end"].get("dateTime", event["end"].get("date")),
                "location": event.get("location", "No Location"),
                "description": event.get("description", "No Description"),
                "organizer": event.get("organizer", {}).get("email", "Unknown"),
            }
            for event in events_result.get("items", [])
        ]

        print("\n🎉 [INFO] Successfully Retrieved Events:", events)

        return JsonResponse(events, safe=False)

    except Exception as e:
        print("\n❌ [ERROR] Exception occurred:", str(e))
        return JsonResponse({"error": str(e)}, status=400)
    
    

def google_calendar_view(request):
    """Render the calendar page"""
    return render(request, "outh/calendar/calendar.html")



# Fetch Event details

@login_required
def get_google_event_details(request, event_id):
    """Fetch complete details of a specific Google Calendar event."""
    try:
        user = request.user
        creds_data = GoogleAuth.objects.filter(user=user).first()

        if not creds_data:
            return JsonResponse({'error': 'Google credentials not found'}, status=400)

        creds = Credentials(
            token=creds_data.access_token,
            refresh_token=creds_data.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=creds_data.scopes,
        )

        # Refresh token if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            creds_data.access_token = creds.token
            creds_data.save()

        # Build Google Calendar API service
        service = build("calendar", "v3", credentials=creds)
        event = service.events().get(calendarId="primary", eventId=event_id).execute()

        # Extract event details
        event_details = {
            "id": event.get("id"),
            "title": event.get("summary", "No Title"),
            "description": event.get("description", "No Description"),
            "start": event["start"].get("dateTime", event["start"].get("date")),
            "end": event["end"].get("dateTime", event["end"].get("date")),
            "location": event.get("location", "No Location"),
            "organizer": event.get("organizer", {}).get("email", "No Organizer"),
            "meeting_link": event.get("hangoutLink", "No Meeting Link"),
            "guests": [
                attendee["email"] for attendee in event.get("attendees", []) if "email" in attendee
            ],
            "reminders": event.get("reminders", {}).get("overrides", []),
            "attachments": [
                {
                    "fileId": attachment.get("fileId"),
                    "title": attachment.get("title"),
                    "mimeType": attachment.get("mimeType"),
                    "fileUrl": attachment.get("fileUrl"),
                }
                for attachment in event.get("attachments", [])
            ]
        }

        return JsonResponse(event_details)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)



# Create Google Calendar Event 
from datetime import datetime

@login_required
@login_required
def create_google_event(request):
    """Create a Google Calendar event when a user clicks on a date."""
    if request.method == "POST":
        try:
            print("🔍 Received request:", request.body)  # DEBUGGING

            data = json.loads(request.body)  # Convert JSON to Python Dict
            print("✅ Parsed JSON Data:", data)  # DEBUGGING

            user = request.user
            creds_data = GoogleAuth.objects.filter(user=user).first()

            if not creds_data:
                print("❌ Google credentials not found for user:", user)
                return JsonResponse({'error': 'Google credentials not found'}, status=400)

            creds = Credentials(
                token=creds_data.access_token,
                refresh_token=creds_data.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                scopes=creds_data.scopes,
            )

            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                creds_data.access_token = creds.token
                creds_data.save()

            title = data.get("title", "Untitled Event")
            description = data.get("description", "")
            location = data.get("location", "")
            start_time = data.get("start")
            end_time = data.get("end")
            guests_emails = data.get("guests", [])
            generate_meeting = data.get("meeting_link", False)
            notify_guests = data.get("notify_guests", False)

            if not start_time or not end_time:
                print("❌ Missing Start or End Time")
                return JsonResponse({"error": "Start and end time are required"}, status=400)

            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)

            print("✅ Event Details:", title, start_dt, end_dt)

            # Send event data to Google Calendar
            service = build("calendar", "v3", credentials=creds)
            event_data = {
                "summary": title,
                "description": description,
                "location": location,
                "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
                "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
                "attendees": [{"email": email} for email in guests_emails],
                "reminders": {"useDefault": False, "overrides": [{"method": "email", "minutes": 10}]} if notify_guests else {},
            }

            if generate_meeting:
                event_data["conferenceData"] = {
                    "createRequest": {
                        "requestId": "meet-" + datetime.now().strftime("%Y%m%d%H%M%S"),
                        "conferenceSolutionKey": {"type": "hangoutsMeet"},
                    }
                }

            event = service.events().insert(
                calendarId="primary",
                body=event_data,
                conferenceDataVersion=1 if generate_meeting else 0
            ).execute()

            print("✅ Google Event Created:", event.get("id"))

            return JsonResponse({
                "message": "Event created successfully",
                "event_id": event.get("id"),
                "meeting_link": event.get("hangoutLink", "No Meeting Link"),
            })

        except json.JSONDecodeError:
            print("❌ JSON Decode Error")
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            print("❌ Exception Occurred:", str(e))
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=400)





# GENERATE AND EXPORT EVENT REPORTS
def gett_google_event_details(event_id, credentials):
    service = build('calendar', 'v3', credentials=credentials)
    event = service.events().get(calendarId='primary', eventId=event_id).execute()

    event_details = {
        "id": event.get("id"),
        "title": event.get("summary", "No Title"),
        "description": event.get("description", "No Description"),
        "start": event["start"].get("dateTime", event["start"].get("date")),
        "end": event["end"].get("dateTime", event["end"].get("date")),
        "location": event.get("location", "No Location"),
        "organizer": event.get("organizer", {}).get("email", "No Organizer"),
        "meeting_link": event.get("hangoutLink", "No Meeting Link"),
        "guests": [
            attendee["email"] for attendee in event.get("attendees", []) if "email" in attendee
        ],
        "reminders": event.get("reminders", {}).get("overrides", []),
        "attachments": [
            {
                "fileId": attachment.get("fileId"),
                "title": attachment.get("title"),
                "mimeType": attachment.get("mimeType"),
                "fileUrl": attachment.get("fileUrl"),
            }
            for attachment in event.get("attachments", [])
        ]
    }

    return event_details

def generate_event_report(request, event_id):
    try:
        # Fetch GoogleAuth instance for the authenticated user
        google_auth = GoogleAuth.objects.get(user=request.user)

        # Debugging: Ensure google_auth contains the expected values
        print(f"Access Token: {google_auth.access_token}")
        print(f"Refresh Token: {google_auth.refresh_token}")

        # Check if refresh_token is available
        if not google_auth.refresh_token:
            return HttpResponse("Refresh token is missing. Please re-authenticate.", status=400)

        # Create Credentials object using the stored access and refresh tokens
        credentials = Credentials(
            token=google_auth.access_token,
            refresh_token=google_auth.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,  # Assuming client_id is stored in your settings
            client_secret=settings.GOOGLE_CLIENT_SECRET  # Assuming client_secret is stored in your settings
        )

        # Debugging: Ensure credentials are being created correctly
        print(f"Credentials: {credentials}")

        # Refresh the token if expired
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
            except Exception as e:
                return HttpResponse(f"Failed to refresh token: {str(e)}", status=500)

        # Fetch the event details from Google Calendar API
        event_details = gett_google_event_details(event_id, credentials)

        # Check if the user requested CSV or PDF export
        export_type = request.GET.get('export', 'csv')  # Default to CSV if no export type provided
        
        if export_type == 'csv':
            return generate_csv_report(event_details)
        elif export_type == 'pdf':
            return generate_pdf_report(event_details)
        else:
            return HttpResponse("Invalid export type.", status=400)

    except GoogleAuth.DoesNotExist:
        return HttpResponse("Google credentials not found. Please authenticate.", status=400)

def generate_csv_report(event_details):
    # Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="event_{event_details["id"]}_report.csv"'
    writer = csv.writer(response)

    # Write header
    writer.writerow(['Event Title', 'Event Description', 'Event Start Date', 'Event End Date', 'Location', 'Organizer', 'Guest Email'])

    # Write event data
    writer.writerow([
        event_details['title'],
        event_details['description'],
        event_details['start'],
        event_details['end'],
        event_details['location'],
        event_details['organizer'],
        ', '.join(event_details['guests'])  # List of guest emails
    ])

    return response

def generate_pdf_report(event_details):
    # Create a PDF response
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(72, 750, f"Google Calendar Event Report for {event_details['title']}")

    # Event details
    p.setFont("Helvetica", 12)
    p.drawString(72, 725, f"Event Description: {event_details['description']}")
    p.drawString(72, 705, f"Start Date: {event_details['start']}")
    p.drawString(72, 685, f"End Date: {event_details['end']}")
    p.drawString(72, 665, f"Location: {event_details['location']}")
    p.drawString(72, 645, f"Organizer: {event_details['organizer']}")

    # Attendees list
    p.drawString(72, 625, f"Attendees:")

    y_position = 605
    for guest in event_details['guests']:
        p.drawString(72, y_position, f"- {guest}")
        y_position -= 20

    # Finalize the PDF
    p.showPage()
    p.save()

    # Return the PDF as response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="event_{event_details["id"]}_report.pdf"'

    return response



# DELETE EVENT

# View to handle event deletion from Google Calendar
@login_required
def delete_event(request, event_id):
    try:
        # Fetch GoogleAuth instance for the authenticated user
        google_auth = GoogleAuth.objects.get(user=request.user)

        # Create Credentials object using the stored access and refresh tokens
        credentials = Credentials(
            token=google_auth.access_token,
            refresh_token=google_auth.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
        )

        # Refresh the token if expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        # Create service to interact with the Google Calendar API
        service = build('calendar', 'v3', credentials=credentials)

        # Delete the event from Google Calendar
        service.events().delete(calendarId='primary', eventId=event_id).execute()

        return JsonResponse({"success": True, "message": "Event deleted successfully!"})

    except GoogleAuth.DoesNotExist:
        return JsonResponse({"success": False, "message": "Google credentials not found. Please authenticate."})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})
