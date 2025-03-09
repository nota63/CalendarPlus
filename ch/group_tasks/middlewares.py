from django.utils.deprecation import MiddlewareMixin
from django.core.files.base import ContentFile
from django.utils.timezone import now
from PIL import Image
from io import BytesIO
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from .models import RecentVisit

class RecentActivityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            url = request.build_absolute_uri()

            # Check if this URL was recently visited
            last_visit = RecentVisit.objects.filter(user=request.user, url=url).first()
            if last_visit:
                last_visit.visited_at = now()
                last_visit.save()
                return

            # Capture screenshot using Selenium
            screenshot_data = self.capture_screenshot(url)

            # Save to database
            visit = RecentVisit(user=request.user, url=url)
            if screenshot_data:
                image = Image.open(BytesIO(screenshot_data))
                buffer = BytesIO()
                image.save(buffer, format="PNG")
                file_content = ContentFile(buffer.getvalue())
                visit.screenshot.save(f"{request.user.id}_{now().timestamp()}.png", file_content)

            visit.save()

            # Keep only last 20 recent visits
            extra_visits = RecentVisit.objects.filter(user=request.user).order_by('-visited_at')
            if extra_visits.count() > 20:
                extra_ids = extra_visits[20:].values_list('id', flat=True)  # Get IDs of extra records
                RecentVisit.objects.filter(id__in=extra_ids).delete()  # Now delete them safely

    def capture_screenshot(self, url):
        """ Captures a screenshot of the given URL using Selenium """
        try:
            options = Options()
            options.headless = True  # Run in headless mode (no UI)
            options.add_argument("--window-size=1280,720")  # Set window size

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            driver.get(url)
            time.sleep(3)  # Wait for the page to load fully

            screenshot = driver.get_screenshot_as_png()  # Capture screenshot

            driver.quit()
            return screenshot
        except Exception as e:
            print(f"Screenshot Capture Error: {e}")
            return None
