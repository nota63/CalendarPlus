from django.utils.deprecation import MiddlewareMixin
from django.core.files.base import ContentFile
from django.utils.timezone import now
import subprocess
from io import BytesIO
from .models import RecentVisit

class RecentActivityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            url = request.build_absolute_uri()

            # Check if URL was recently visited
            last_visit = RecentVisit.objects.filter(user=request.user, url=url).first()
            if last_visit:
                last_visit.visited_at = now()
                last_visit.save()
                return

            # Save visit entry
            visit = RecentVisit.objects.create(user=request.user, url=url)

            # Capture screenshot using webkit2png
            screenshot_data = self.capture_screenshot(url)
            if screenshot_data:
                visit.screenshot.save(f"{request.user.id}_{now().timestamp()}.png", screenshot_data)

            visit.save()

            # Keep only last 20 recent visits
            extra_visits = RecentVisit.objects.filter(user=request.user).order_by('-visited_at')
            if extra_visits.count() > 20:
                extra_ids = extra_visits[20:].values_list('id', flat=True)
                RecentVisit.objects.filter(id__in=extra_ids).delete()

    def capture_screenshot(self, url):
        """ Captures a screenshot using webkit2png """
        try:
            output_file = f"/tmp/{now().timestamp()}.png"  # Temporary file path

            # Run webkit2png command
            subprocess.run(["webkit2png", "-o", output_file, url], check=True)

            # Read the screenshot file
            with open(output_file, "rb") as file:
                return ContentFile(file.read(), name="screenshot.png")

        except Exception as e:
            print(f"Screenshot Capture Error: {e}")
            return None
