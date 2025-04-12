# middleware.py

from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RecentActivity  # Custom model to store activity
class ActivityCaptureMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            model_name, object_id = self._extract_model_info(view_func, view_kwargs)

            request._capture_activity_meta = {
                'user': request.user,
                'path': request.get_full_path(),
                'method': request.method,
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'activity_type': self.get_activity_type(request.method),
                'model_name': model_name,
                'object_id': str(object_id) if object_id else None
            }
        return None

    def process_response(self, request, response):
        if hasattr(request, '_capture_activity_meta') and response.status_code in [200, 201, 204]:
            meta = request._capture_activity_meta

            RecentActivity.objects.create(
                user=meta['user'],
                path=meta['path'],
                method=meta['method'],
                ip_address=meta['ip_address'],
                user_agent=meta['user_agent'],
                activity_type=meta['activity_type'],
                model_name=meta['model_name'],
                object_id=meta['object_id'],
                timestamp=now()
            )
        return response

    def get_activity_type(self, method):
        return {
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete',
        }.get(method, 'other')

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def _extract_model_info(self, view_func, view_kwargs):
        """
        Attempts to extract model name and object_id from view or kwargs.
        """
        try:
            view_class = getattr(view_func, 'view_class', None)

            if view_class:
                model = getattr(view_class, 'queryset', None)
                if model:
                    model_name = model.model.__name__
                else:
                    # Try get_model from serializer_class if defined
                    serializer = getattr(view_class, 'serializer_class', None)
                    if serializer and hasattr(serializer.Meta, 'model'):
                        model_name = serializer.Meta.model.__name__
                    else:
                        model_name = None
            else:
                model_name = None

            object_id = view_kwargs.get("pk") or view_kwargs.get("id") or None

            return model_name, object_id
        except Exception:
            return None, None