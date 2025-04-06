from django.conf import settings
import logging
logger = logging.getLogger(__name__)

class ImpersonationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
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

        response = self.get_response(request)
        return response
