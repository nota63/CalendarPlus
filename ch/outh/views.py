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
from googleapiclient.http import MediaIoBaseUpload
import io
from django.views.decorators.csrf import csrf_exempt
import logging
from googleapiclient.errors import HttpError

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
                 "https://www.googleapis.com/auth/calendar","https://www.googleapis.com/auth/drive.file"],
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
             "https://www.googleapis.com/auth/calendar.events","https://www.googleapis.com/auth/drive.file"],
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


# generate event report
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


# ATTACH ATTACHMENTS



@login_required
def add_event_attachment(request, event_id):
    if request.method == "POST":
        try:
            google_auth = GoogleAuth.objects.get(user=request.user)

            credentials = Credentials(
                token=google_auth.access_token,
                refresh_token=google_auth.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                scopes=["https://www.googleapis.com/auth/calendar.events", 
                        "https://www.googleapis.com/auth/drive.file"]  # ✅ FIXED SCOPES
            )

            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())

            service = build('calendar', 'v3', credentials=credentials)

            # Get the uploaded file
            file = request.FILES.get('attachment')
            if not file:
                return JsonResponse({"success": False, "message": "No file uploaded!"})

            # Upload the file to Google Drive
            drive_service = build('drive', 'v3', credentials=credentials)
            file_metadata = {'name': file.name}
            
            # Convert the file to a stream for upload
            file_stream = io.BytesIO(file.read())
            media = MediaIoBaseUpload(file_stream, mimetype=file.content_type, resumable=True)

            uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()

            # Attach the file to the event
            event = service.events().get(calendarId='primary', eventId=event_id).execute()
            event.setdefault('attachments', []).append({
                "fileId": uploaded_file['id'],
                "title": file.name,
                "fileUrl": uploaded_file['webViewLink'],
                "mimeType": file.content_type
            })

            updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()

            return JsonResponse({"success": True, "message": "Attachment added successfully!", "attachment": uploaded_file['webViewLink']})

        except GoogleAuth.DoesNotExist:
            return JsonResponse({"success": False, "message": "Google credentials not found. Please authenticate."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method."})



# HANDLE DUPLICATION OF EVENT

@login_required
def duplicate_event(request, event_id):
    try:
        # Fetch user's Google Auth credentials
        google_auth = GoogleAuth.objects.get(user=request.user)

        # Create OAuth2 credentials
        credentials = Credentials(
            token=google_auth.access_token,
            refresh_token=google_auth.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=[
                "https://www.googleapis.com/auth/calendar.events",
                "https://www.googleapis.com/auth/drive.file"
            ]
        )

        # Refresh token if expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        # Initialize Google Calendar service
        service = build('calendar', 'v3', credentials=credentials)

        # Fetch the original event details
        original_event = service.events().get(calendarId='primary', eventId=event_id).execute()

        # Extract details for duplication
        duplicated_event = {
            "summary": original_event.get("summary", "Duplicated Event"),
            "location": original_event.get("location", ""),
            "description": original_event.get("description", ""),
            "start": original_event["start"],  # Start date & time
            "end": original_event["end"],  # End date & time
            "attendees": original_event.get("attendees", []),  # Guests
            "reminders": original_event.get("reminders", {}),
            "conferenceData": original_event.get("conferenceData", {}),  # Meeting link
            "attachments": original_event.get("attachments", []),  # Attachments
        }

        # ✅ Create the new duplicated event
        new_event = service.events().insert(
            calendarId="primary",
            body=duplicated_event,
            conferenceDataVersion=1,  # Required for Google Meet links
            supportsAttachments=True
        ).execute()

        return JsonResponse({
            "success": True,
            "message": "Event duplicated successfully!",
            "new_event_id": new_event["id"],
            "event_link": new_event["htmlLink"]
        })

    except GoogleAuth.DoesNotExist:
        return JsonResponse({"success": False, "message": "Google credentials not found. Please authenticate."})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})
    

# EDIT THE EVENT



logger = logging.getLogger(__name__)  # 🔥 Logging for debugging
@csrf_exempt
@login_required
def edit_google_event(request, event_id):
    """Handles both GET (fetch event details) and POST (update event) requests."""

    try:
        logger.info(f"🔹 Processing Google Event Edit for event_id: {event_id}")

        # ✅ Fetch user credentials
        try:
            google_auth = GoogleAuth.objects.get(user=request.user)
        except GoogleAuth.DoesNotExist:
            logger.error("❌ GoogleAuth credentials not found!")
            return JsonResponse({"success": False, "message": "Google authentication not found!"}, status=401)

        # ✅ Load credentials
        credentials = Credentials(
            token=google_auth.access_token,
            refresh_token=google_auth.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=google_auth.scopes
        )

        # 🔄 **Refresh token if expired**
        if not credentials.valid or credentials.expired:
            if credentials.refresh_token:
                try:
                    logger.info("🔄 Refreshing Google OAuth token...")
                    credentials.refresh(Request())

                    # ✅ **Save new access token**
                    google_auth.access_token = credentials.token
                    google_auth.save()
                    logger.info("✅ Token refreshed successfully!")
                except Exception as e:
                    logger.error(f"❌ Token refresh failed: {e}")
                    return JsonResponse({"success": False, "message": f"Failed to refresh token: {str(e)}"}, status=401)
            else:
                logger.error("❌ No refresh token available!")
                return JsonResponse({"success": False, "message": "No refresh token available. Please re-authenticate."}, status=401)

        # 🔥 **Initialize Google Calendar API**
        service = build("calendar", "v3", credentials=credentials)

        # ✅ **Handle GET request - Fetch event details**
        if request.method == "GET":
            try:
                logger.info(f"📡 Fetching event details for {event_id}")
                event = service.events().get(calendarId="primary", eventId=event_id).execute()
                return JsonResponse({"success": True, "event": event})
            except HttpError as e:
                logger.error(f"❌ Google API Error while fetching event: {e}")
                return JsonResponse({"success": False, "message": "Error fetching event from Google Calendar."}, status=400)
            except Exception as e:
                logger.error(f"❌ Unexpected error fetching event: {e}")
                return JsonResponse({"success": False, "message": f"Unexpected error: {str(e)}"}, status=400)

        # ✅ **Handle POST request - Update event**
        elif request.method == "POST":
            try:
                # ✅ **Parse JSON request body**
                data = json.loads(request.body.decode("utf-8"))
                logger.info(f"📥 Received update request: {data}")

                # 🔎 **Ensure all required fields are present**
                required_fields = ["title", "start", "end"]
                for field in required_fields:
                    if field not in data or not data[field].strip():
                        logger.error(f"❌ Missing required field: {field}")
                        return JsonResponse({"success": False, "message": f"Missing required field: {field}"}, status=400)

                # ✅ **Ensure datetime format is correct (ISO 8601)**
                start_time = data["start"].strip()
                end_time = data["end"].strip()
                if "T" not in start_time or "T" not in end_time:
                    logger.error("❌ Invalid datetime format. Must be ISO 8601.")
                    return JsonResponse({"success": False, "message": "Invalid datetime format. Must be ISO 8601."}, status=400)

                # ✅ **Process guests data**
                guests = data.get("guests", [])
                # Handle both comma-separated strings and list inputs
                if isinstance(guests, str):
                    guests = [email.strip() for email in guests.split(',') if email.strip()]
                elif not isinstance(guests, list):
                    guests = []

                # ✅ **Process reminders safely**
                reminder_minutes = 10  # default value
                try:
                    reminder_minutes = int(data.get("reminders", 10))
                except ValueError:
                    logger.warning("⚠️ Invalid reminder value, using default 10 minutes")

                # ✅ **Prepare event data**
                event_data = {
                    "summary": data["title"].strip(),
                    "description": data.get("description", "").strip(),
                    "start": {"dateTime": start_time, "timeZone": "UTC"},
                    "end": {"dateTime": end_time, "timeZone": "UTC"},
                    "location": data.get("location", "").strip(),
                    "attendees": [{"email": email} for email in guests if email],
                    "reminders": {
                        "useDefault": False,
                        "overrides": [{"method": "email", "minutes": reminder_minutes}]
                    },
                }

                logger.info(f"📡 Sending event update request to Google: {event_data}")

                # 🔥 **Update the event in Google Calendar**
                updated_event = service.events().update(
                    calendarId="primary", eventId=event_id, body=event_data
                ).execute()

                logger.info("✅ Event updated successfully!")
                return JsonResponse({"success": True, "message": "Event updated successfully!", "event": updated_event})

            except json.JSONDecodeError:
                logger.error("❌ Invalid JSON data received")
                return JsonResponse({"success": False, "message": "Invalid JSON data"}, status=400)
            except HttpError as e:
                logger.error(f"❌ Google API Error while updating event: {e}")
                return JsonResponse({"success": False, "message": "Error updating event in Google Calendar."}, status=400)
            except Exception as e:
                logger.error(f"❌ Unexpected error updating event: {e}")
                return JsonResponse({"success": False, "message": f"Unexpected error: {str(e)}"}, status=400)

    except Exception as e:
        logger.critical(f"🔥 Unexpected critical error: {e}", exc_info=True)
        return JsonResponse({"success": False, "message": f"Unexpected error: {str(e)}"}, status=500)
    


# MANAGE ACTIONS (GOING/YES/NO/MAY-BE)
@csrf_exempt
@login_required
def update_event_response(request, event_id):
    """Updates the attendee's response for a Google Calendar event without overriding other event details."""
    try:
        logger.info(f"🔹 Processing response update for event_id: {event_id}")

        # ✅ Fetch user credentials
        google_auth = GoogleAuth.objects.filter(user=request.user).first()
        if not google_auth:
            logger.error("❌ GoogleAuth credentials not found!")
            return JsonResponse({"success": False, "message": "Google authentication not found!"}, status=401)

        # ✅ Load credentials
        credentials = Credentials(
            token=google_auth.access_token,
            refresh_token=google_auth.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=google_auth.scopes
        )

        # 🔄 **Refresh token if expired**
        if credentials.expired and credentials.refresh_token:
            try:
                logger.info("🔄 Refreshing Google OAuth token...")
                credentials.refresh(Request())
                google_auth.access_token = credentials.token
                google_auth.save()
                logger.info("✅ Token refreshed successfully!")
            except Exception as e:
                logger.error(f"❌ Token refresh failed: {e}")
                return JsonResponse({"success": False, "message": f"Failed to refresh token: {str(e)}"}, status=401)

        # 🔥 **Initialize Google Calendar API**
        service = build("calendar", "v3", credentials=credentials)

        # ✅ **Parse JSON request body**
        try:
            data = json.loads(request.body.decode("utf-8"))
            response_choice = data.get("response", "").strip().lower()
        except json.JSONDecodeError:
            logger.error("❌ Invalid JSON data received")
            return JsonResponse({"success": False, "message": "Invalid JSON data"}, status=400)

        # ✅ **Map response to Google Calendar API values**
        response_map = {
            "yes": "accepted",
            "maybe": "tentative",
            "no": "declined",
        }

        if response_choice not in response_map:
            logger.error(f"❌ Invalid response: {response_choice}")
            return JsonResponse({"success": False, "message": "Invalid response choice."}, status=400)

        # ✅ **Fetch existing event data**
        try:
            event = service.events().get(calendarId="primary", eventId=event_id).execute()
        except HttpError as e:
            logger.error(f"❌ Google API Error while fetching event: {e}")
            return JsonResponse({"success": False, "message": "Error fetching event from Google Calendar."}, status=400)

        # ✅ **Extract required event fields**
        start_time = event.get("start")
        end_time = event.get("end")

        if not start_time or not end_time:
            logger.error("❌ Event is missing start or end time!")
            return JsonResponse({"success": False, "message": "Event is missing start or end time."}, status=400)

        # ✅ **Get the current user’s email from event attendees**
        user_email = None
        if "attendees" in event:
            for attendee in event["attendees"]:
                if attendee.get("self"):  # Google's API marks the logged-in user as "self"
                    user_email = attendee["email"]
                    break

        if not user_email:
            logger.error("❌ Could not determine user's email from the event.")
            return JsonResponse({"success": False, "message": "Could not find your email in the event attendees."}, status=400)

        # ✅ **Update attendee's response**
        attendees = event.get("attendees", [])
        updated = False
        for attendee in attendees:
            if attendee["email"] == user_email:
                attendee["responseStatus"] = response_map[response_choice]
                updated = True
                break

        if not updated:
            logger.error("❌ User is not an attendee of this event!")
            return JsonResponse({"success": False, "message": "You are not an attendee of this event."}, status=400)

        # ✅ **Preserve all existing event details**
        updated_event_data = {
            "summary": event.get("summary", "No Title"),
            "description": event.get("description", "No Description"),
            "location": event.get("location", ""),
            "start": start_time,
            "end": end_time,
            "attendees": attendees,  # ✅ **Update attendees list**
            "reminders": event.get("reminders", {}),
            "hangoutLink": event.get("hangoutLink", ""),
            "attachments": event.get("attachments", []),
        }

        # 🔥 **Send update request**
        try:
            updated_event = service.events().update(
                calendarId="primary",
                eventId=event_id,
                body=updated_event_data
            ).execute()
            logger.info("✅ Event response updated successfully!")
            return JsonResponse({"success": True, "message": "Response updated successfully!", "event": updated_event})
        except HttpError as e:
            logger.error(f"❌ Google API Error while updating response: {e}")
            return JsonResponse({"success": False, "message": "Error updating response in Google Calendar."}, status=400)

    except Exception as e:
        logger.critical(f"🔥 Unexpected critical error: {e}", exc_info=True)
        return JsonResponse({"success": False, "message": f"Unexpected error: {str(e)}"}, status=500)
    


# GENERATE INVITE LINK
@login_required
def get_event_invite_link(request, event_id):
    """Generate a Google Calendar invite link for an event."""
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

        # Get event details
        event_title = event.get("summary", "No Title")
        event_description = event.get("description", "No Description")
        event_start = event["start"].get("dateTime", event["start"].get("date"))
        event_end = event["end"].get("dateTime", event["end"].get("date"))
        event_location = event.get("location", "")

        # ✅ Generate Google Calendar Invite Link
        invite_link = f"https://calendar.google.com/calendar/render?action=TEMPLATE"
        invite_link += f"&text={event_title}"
        invite_link += f"&details={event_description}"
        invite_link += f"&location={event_location}"
        invite_link += f"&dates={event_start.replace('-', '').replace(':', '').replace('+', 'Z')}/{event_end.replace('-', '').replace(':', '').replace('+', 'Z')}"

        return JsonResponse({'success': True, 'event_link': invite_link})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    


# Invite Link 
import urllib.parse

@login_required
def generate_google_booking_link(request, event_id):
    """Generate a Google Calendar invite link with full event details for booking."""
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
        title = event.get("summary", "No Title")
        start_time = event["start"].get("dateTime", event["start"].get("date"))
        end_time = event["end"].get("dateTime", event["end"].get("date"))
        location = event.get("location", "")
        description = event.get("description", "")
        organizer = event["organizer"].get("email", "")
        attendees = [a["email"] for a in event.get("attendees", [])]
        reminders = event.get("reminders", {}).get("overrides", [])

        # Generate Google Calendar booking link in the correct format
        base_url = "https://calendar.google.com/calendar/r/eventedit"
        
        # Convert dateTime into proper format: YYYYMMDDTHHmmSSZ
        start_time_formatted = start_time.replace(":", "").replace("-", "").replace("+", "Z")
        end_time_formatted = end_time.replace(":", "").replace("-", "").replace("+", "Z")

        # Create the query parameters for the event
        query_params = {
            "text": title,
            "dates": f"{start_time_formatted}/{end_time_formatted}",
            "details": description,
            "location": location,
            "add": ",".join(attendees),
            "trp": "false",
            "sprop": "https://calendar.google.com/calendar/",
            "sprop=name":"Google Calendar",
        }

        # Encode parameters
        invite_link = f"{base_url}?{urllib.parse.urlencode(query_params)}"

        return JsonResponse({'success': True, 'event_link': invite_link})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    


# PUBLISH THE EVENT
@login_required
def publish_event(request, event_id):
    """Generate the Google Calendar event links and HTML code to publish the event."""
    try:
        # Fetch user credentials
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

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            creds_data.access_token = creds.token
            creds_data.save()

        # Build the Google Calendar service
        service = build("calendar", "v3", credentials=creds)
        event = service.events().get(calendarId="primary", eventId=event_id).execute()

        # Extract event details
        start_time = event["start"].get("dateTime", event["start"].get("date"))
        end_time = event["end"].get("dateTime", event["end"].get("date"))
        title = event.get("summary", "No Title")
        description = event.get("description", "")
        location = event.get("location", "")
        meeting_link = event.get("hangoutLink", "")
        
        # Get organizer email
        organizer_email = event.get("organizer", {}).get("email", "No Organizer Email")

        # Get guest emails
        guests = event.get("attendees", [])
        guest_emails = [attendee.get("email") for attendee in guests if "email" in attendee]

        # Format the start and end times properly for Google Calendar URL
        start_time = start_time.replace(":", "").replace("-", "").replace("T", "")  # Clean up the time
        end_time = end_time.replace(":", "").replace("-", "").replace("T", "")  # Clean up the time

        # Generate the Google Calendar event link (for adding to calendar)
        calendar_url = f"https://calendar.google.com/calendar/event?action=TEMPLATE&text={title}&details={description}&location={location}&dates={start_time}/{end_time}&sf=true&output=xml"

        # Generate the HTML code for embedding the Google Calendar button
        tmeid = event.get("id")
        embed_code = f'<a target="_blank" href="https://calendar.google.com/calendar/event?action=TEMPLATE&tmeid={tmeid}&tmsrc={organizer_email}"><img border="0" src="https://www.google.com/calendar/images/ext/gc_button1_en-GB.gif"></a>'

        # Return response with generated link and embed code
        return JsonResponse({
            "calendar_url": calendar_url,
            "embed_code": embed_code,
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# CHANGE EVENT OWNER
@login_required
def change_event_owner(request, event_id):
    """Transfer event ownership by adding a new owner as a guest and providing event details."""
    if request.method == "POST":
        new_owner_email = request.POST.get("new_owner_email")

        if not new_owner_email:
            return JsonResponse({"error": "New owner email is required"}, status=400)

        try:
            # Fetch user's Google credentials
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

            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                creds_data.access_token = creds.token
                creds_data.save()

            # Build Google Calendar service
            service = build("calendar", "v3", credentials=creds)

            # Get event details
            event = service.events().get(calendarId="primary", eventId=event_id).execute()

            # Check if the current user is the organizer
            current_organizer = event.get("organizer", {}).get("email")
            if current_organizer != request.user.email:
                return JsonResponse({"error": "Only the current organizer can change ownership"}, status=403)

            # Add the new owner as a guest
            attendees = event.get("attendees", [])
            if not any(att["email"] == new_owner_email for att in attendees):
                attendees.append({"email": new_owner_email})

            event["attendees"] = attendees

            # Update the event with the new attendee
            updated_event = service.events().update(
                calendarId="primary", eventId=event_id, body=event, sendUpdates="all"
            ).execute()

            # Provide updated event details
            event_details = {
                "id": updated_event.get("id"),
                "title": updated_event.get("summary", "No Title"),
                "description": updated_event.get("description", "No Description"),
                "start": updated_event["start"].get("dateTime", updated_event["start"].get("date")),
                "end": updated_event["end"].get("dateTime", updated_event["end"].get("date")),
                "location": updated_event.get("location", "No Location"),
                "organizer": updated_event.get("organizer", {}).get("email", "No Organizer"),
                "meeting_link": updated_event.get("hangoutLink", "No Meeting Link"),
                "guests": [
                    attendee["email"] for attendee in updated_event.get("attendees", []) if "email" in attendee
                ],
            }

            return JsonResponse({
                "message": "New owner added as a guest. They need to accept the invite to become the owner.",
                "event_details": event_details
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


# HANDLE CUSTOM REMINDERS

@csrf_exempt
@login_required
def save_custom_reminder(request, event_id, reminder_time):
    if request.method == "POST":
        try:
            # Retrieve user's GoogleAuth credentials from the database
            google_auth = GoogleAuth.objects.filter(user=request.user).first()
            if not google_auth:
                return JsonResponse({"success": False, "error": "Google authentication not found."}, status=400)

            # Construct credentials object
            creds = Credentials(
                token=google_auth.access_token,
                refresh_token=google_auth.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                scopes=google_auth.scopes
            )

            # Connect to Google Calendar API
            service = build("calendar", "v3", credentials=creds)

            # Fetch the existing event from Google Calendar
            event = service.events().get(calendarId="primary", eventId=event_id).execute()

            # Update reminder settings
            event["reminders"] = {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": int(reminder_time)},  # Custom popup reminder
                    {"method": "email", "minutes": int(reminder_time)}   # Email notification
                ]
            }

            # Update the event in Google Calendar
            updated_event = service.events().update(calendarId="primary", eventId=event_id, body=event).execute()

            return JsonResponse({"success": True, "message": "Reminder updated successfully!"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)