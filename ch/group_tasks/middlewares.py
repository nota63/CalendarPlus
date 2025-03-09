from django.utils.deprecation import MiddlewareMixin
from django.core.files.base import ContentFile
from django.utils.timezone import now
import os
import time
import pyautogui
from PIL import Image
from io import BytesIO
from .models import RecentVisit

class RecentActivityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            url = request.build_absolute_uri()
            print(f"📌 Processing Request for URL: {url}")

            # Ignore static assets like CSS, JS, and images
            if url.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif')):
                print(f"🛑 Ignoring asset file: {url}")
                return

            # Check if the URL was recently visited
            last_visit = RecentVisit.objects.filter(user=request.user, url=url).first()
            if last_visit:
                print(f"🔄 URL already visited. Updating timestamp.")
                last_visit.visited_at = now()
                last_visit.save()
                return

            # Save visit entry
            print(f"✅ Saving new visit entry...")
            visit = RecentVisit.objects.create(user=request.user, url=url)

            # ✅ **Wait for the page to fully load before capturing screenshot**
            time.sleep(1.5)  # 🔥 Adjust this delay if needed

            # Capture screenshot using PyAutoGUI
            print(f"📸 Capturing full-screen screenshot for: {url}")
            screenshot_data = self.capture_screenshot()

            if screenshot_data:
                print(f"✅ Screenshot captured successfully! Saving it to the database...")
                visit.screenshot.save(f"{request.user.id}_{now().timestamp()}.png", screenshot_data)
            else:
                print(f"❌ Failed to capture screenshot.")

            visit.save()
            print(f"✅ Visit saved successfully!")

            # Keep only the last 20 recent visits
            extra_visits = RecentVisit.objects.filter(user=request.user).order_by('-visited_at')
            if extra_visits.count() > 20:
                extra_ids = extra_visits[20:].values_list('id', flat=True)
                print(f"🗑️ Deleting old visits: {extra_ids}")
                RecentVisit.objects.filter(id__in=extra_ids).delete()

    def capture_screenshot(self):
        """ Captures a full-screen screenshot using PyAutoGUI & Pillow (NO WebDriver Needed) """
        try:
            # Take a screenshot of the entire screen
            screenshot = pyautogui.screenshot()

            # Convert to bytes
            img_io = BytesIO()
            screenshot.save(img_io, format="PNG")
            img_io.seek(0)

            print(f"✅ Screenshot successfully converted to bytes.")
            return ContentFile(img_io.read(), name=f"screenshot_{now().timestamp()}.png")

        except Exception as e:
            print(f"❌ Screenshot Capture Error: {e}")
            return None
