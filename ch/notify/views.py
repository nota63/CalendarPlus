from django.shortcuts import render
from django.http import JsonResponse
import json
from .models import PushSubscription
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PushSubscription
from pywebpush import webpush, WebPushException
import json
from django.conf import settings
# Create your views here.

@csrf_exempt
def save_subscription(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        endpoint = data.get('endpoint')
        p256dh = data.get('p256dh')
        auth = data.get('auth')

        # Save the subscription in the database
        PushSubscription.objects.create(
            endpoint=endpoint,
            p256dh=p256dh.decode('utf-8'),  # Decode from base64 if necessary
            auth=auth.decode('utf-8')  # Decode from base64 if necessary
        )

        return JsonResponse({"status": "Subscription saved"})
    return JsonResponse({"status": "Error", "message": "Invalid request method"})

def send_push_notification(request):
    if request.method == "POST":
        # Get the form data
        title = request.POST.get('title')
        body = request.POST.get('body')
        icon = request.POST.get('icon', None)
        badge = request.POST.get('badge', None)

        # Get the first subscription object from the database
        subscription = PushSubscription.objects.first()

        if subscription is None:
            return JsonResponse({"status": "Error", "error": "No subscriptions found."})

        # Prepare the push notification message
        message = {
            "title": title,
            "body": body,
            "icon": icon if icon else "default_icon.png",  # Set a default if no icon is provided
            "badge": badge if badge else "default_badge.png",  # Default badge if none provided
        }

        try:
            # Send the push notification
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {
                        "p256dh": subscription.p256dh,
                        "auth": subscription.auth,
                    }
                },
                data=json.dumps(message),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": "mailto:your-email@example.com"}
            )
            return JsonResponse({"status": "Notification sent"})
        except WebPushException as e:
            return JsonResponse({"status": "Error", "error": str(e)})

    # Render the form on GET request
    return render(request, 'notify/send_notification_form.html')