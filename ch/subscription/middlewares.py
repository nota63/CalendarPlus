from django.conf import settings
import logging
logger = logging.getLogger(__name__)

# class ImpersonationMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         logger.debug("🔥 ImpersonationMiddleware executing...")

#         impersonator_id = request.session.get('impersonator_id')
#         impersonator_name = request.session.get('impersonator_name')

#         logger.debug(f"Impersonator ID: {impersonator_id}")
#         logger.debug(f"Impersonator Name: {impersonator_name}")

#         if impersonator_id:
#             request.impersonating = True
#             request.impersonator_name = impersonator_name
#         else:
#             request.impersonating = False
#             request.impersonator_name = None

#         response = self.get_response(request)
#         return response


from django.utils.deprecation import MiddlewareMixin
from django.template.loader import render_to_string
class ImpersonationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        logger.debug("🔥 ImpersonationMiddleware executing...")

        impersonator_id = request.session.get('impersonator_id')
        impersonator_name = request.session.get('impersonator_name')

        logger.debug(f"Impersonator ID: {impersonator_id}")
        logger.debug(f"Impersonator Name: {impersonator_name}")

        if impersonator_id:
            request.impersonating = True
            request.impersonator_name = impersonator_name
        else:
            request.impersonating = False
            request.impersonator_name = None

    def process_response(self, request, response):
        if (
            getattr(request, 'impersonating', False) and
            'text/html' in response.get('Content-Type', '') and
            hasattr(response, 'content')
        ):
            try:
                banner_html = render_to_string("partials/impersonation_alert.html", {"request": request})
                content = response.content.decode("utf-8")

                if "</body>" in content:
                    logger.debug("✨ Injecting impersonation banner into HTML...")
                    content = content.replace("</body>", banner_html + "</body>")
                    response.content = content.encode("utf-8")
            except Exception as e:
                logger.error(f"💥 Failed to inject impersonation banner: {e}")

        return response