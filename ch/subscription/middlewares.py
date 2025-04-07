from django.conf import settings
import logging
from .models import HelpRequest, ImpersonationActivityLog
from django.urls import resolve
import logging
import uuid
from accounts.models import Organization

logger = logging.getLogger(__name__)



from django.utils.deprecation import MiddlewareMixin
from django.template.loader import render_to_string


# class ImpersonationMiddleware(MiddlewareMixin):
#     def process_request(self, request):
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

#     def process_response(self, request, response):
#         if (
#             getattr(request, 'impersonating', False) and
#             'text/html' in response.get('Content-Type', '') and
#             hasattr(response, 'content')
#         ):
#             try:
#                 banner_html = render_to_string("partials/impersonation_alert.html", {"request": request})
#                 content = response.content.decode("utf-8")

#                 if "</body>" in content:
#                     logger.debug("✨ Injecting impersonation banner into HTML...")
#                     content = content.replace("</body>", banner_html + "</body>")
#                     response.content = content.encode("utf-8")
#             except Exception as e:
#                 logger.error(f"💥 Failed to inject impersonation banner: {e}")

#         return response


# Updated Middleware for impersonation
logger = logging.getLogger(__name__)

class ImpersonationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        logger.debug("🔥 ImpersonationMiddleware executing...")

        impersonator_id = request.session.get('impersonator_id')
        impersonator_name = request.session.get('impersonator_name')
        help_request_id = request.session.get('help_request_id')
        org_id = request.session.get('organization_id')

        request.impersonating = bool(impersonator_id)
        request.impersonator_name = impersonator_name

        if request.impersonating:
            logger.debug(f"👤 Impersonating as: {impersonator_name}")

            # Log activity only for actual admin actions
            try:
                # Skip logging for static files or health checks
                if request.path.startswith("/static/") or "health" in request.path:
                    return

                help_request = HelpRequest.objects.get(id=uuid.UUID(help_request_id))
                organization = Organization.objects.get(id=org_id)
                admin_user = request.user

                log = ImpersonationActivityLog.objects.create(
                    admin=admin_user,
                    organization=organization,
                    help_request=help_request,
                    path=request.path,
                    method=request.method,
                    request_data=request.POST.dict() if request.method == 'POST' else request.GET.dict(),
                    user_agent=request.META.get("HTTP_USER_AGENT", "")
                )

                logger.debug(f"📥 Logged impersonation activity: {log}")

            except Exception as e:
                logger.warning(f"⚠️ Failed to log impersonation activity: {e}")

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