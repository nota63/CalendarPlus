from django.utils.deprecation import MiddlewareMixin
from django.core.files.base import ContentFile
from django.utils.timezone import now
from PIL import Image
from io import BytesIO
import asyncio
from pyppeteer import launch
from .models import RecentVisit

class RecentActivityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            url = request.build_absolute_uri()
            
            # Check if this URL was recently visited (avoid duplicate entries)
            last_visit = RecentVisit.objects.filter(user=request.user, url=url).first()
            if last_visit:
                last_visit.visited_at = now()
                last_visit.save()
                return
            
            # Capture screenshot asynchronously
            screenshot_data = asyncio.run(self.capture_screenshot(url))
            
            # Save to database
            visit = RecentVisit(user=request.user, url=url)
            if screenshot_data:
                image = Image.open(BytesIO(screenshot_data))
                buffer = BytesIO()
                image.save(buffer, format="PNG")
                file_content = ContentFile(buffer.getvalue())
                visit.screenshot.save(f"{request.user.id}_{now().timestamp()}.png", file_content)

            visit.save()

            # 🔥 Fix: Delete only extra records properly
            extra_visits = RecentVisit.objects.filter(user=request.user).order_by('-visited_at')
            if extra_visits.count() > 20:
                extra_ids = extra_visits[20:].values_list('id', flat=True)  # Get IDs of extra records
                RecentVisit.objects.filter(id__in=extra_ids).delete()  # Now delete them safely

    async def capture_screenshot(self, url):
        """ Captures a screenshot of the given URL """
        try:
            browser = await launch(headless=True)
            page = await browser.newPage()
            await page.setViewport({"width": 1280, "height": 720})  
            await page.goto(url)
            screenshot = await page.screenshot()
            await browser.close()
            return screenshot
        except Exception as e:
            print(f"Screenshot Capture Error: {e}")
            return None
