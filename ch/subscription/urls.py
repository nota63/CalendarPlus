from django.urls import path
from .views import *

urlpatterns=[
    path('initiate_payment/',initiate_payment, name='initiate_payment'),
    path('initiate_payment_for_plan/',initiate_payment_for_plan, name='initiate_payment_for_plan'),
    path('payment-success/',payment_success, name='payment_success'),
    path('raise-help-request-live/<int:org_id>/',raise_help_request, name='raise_help_request_live'),
    path('fetch-my-help-requests/<int:org_id>/',fetch_user_help_requests, name='fetch_my_help_requests'),
    path('fetch-all-help-requests/<int:org_id>/',fetch_all_help_requests_by_org, name='fetch_all_help_requests'),
    path('get-help-request-detail/<uuid:uuid>/',fetch_help_request_detail, name='fetch_help_request_detail'),
    path(
        'login-as-user/<int:org_id>/<uuid:uuid>/<int:user_id>/',
        login_as_user,
        name='login_as_user'
    ),
    path('stop_impersonation/',stop_impersonation, name='stop_impersonation'),
    path('start_impersonation/<int:org_id>/<uuid:uuid>/<int:user_id>/',start_impersonation, name='start_impersonation'),
    path('fetch-impersonation-logs/<uuid:help_id>/',fetch_impersonation_logs_by_help_id, name='fetch_impersonation_logs_by_help_id'),




]
