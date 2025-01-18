

from django.urls import path
from .views import UserMeetingContactsView
from .views import *

urlpatterns = [
       path('contacts/<int:org_id>/', UserMeetingContactsView.as_view(), name='user_meeting_contacts'),

        
       path('add_to_contacts/<int:org_id>/<int:user_id>/', add_to_contacts, name='add_to_contacts'),

       path('organization/<int:org_id>/contacts/', ContactsListView.as_view(), name='contacts_list'),

       path('organization/<int:org_id>/user/<int:user_id>/details/', UserDetailsView.as_view(), name='user_details'),

       path('organization/<int:org_id>/contacts/filter/', FilterContactsView.as_view(), name='filter_contacts'),

       path('send_email/<int:org_id>/<int:user_id>/', SendEmailView.as_view(), name='send_email'),

       # retrive emails 
       path('emails/<int:org_id>/<int:user_id>/', FetchEmailsView.as_view(), name='fetch_emails'),

       path('contacts/email-detail/<int:org_id>/<int:user_id>/<int:email_id>/', EmailDetailView.as_view(), name='email_detail'),

       path('emails/download/<int:org_id>/<int:user_id>/<int:email_id>/', download_email_pdf, name='download_email_pdf'),

       path('contacts/delete-email/<int:org_id>/<int:user_id>/<int:email_id>/',delete_email, name='delete_email'),

       # Email analysis
       path('email-analysis/<int:org_id>/<int:user_id>/<int:email_id>/',email_analysis_view, name='email_analysis'),

       # edit and resend the email
       path('edit-resend-email/<int:org_id>/<int:user_id>/<int:email_id>/', EditAndResendEmailView.as_view(), name='edit_resend_email'),

       # schedule email
       path('schedule-email/<int:org_id>/<int:user_id>/', ScheduleEmailView.as_view(), name='schedule-email'),

       path(
        'email/success/<int:org_id>/<int:participant_id>/<str:organization_name>/<str:participant_name>/<str:message>/<str:schedule_time>/<str:template_style>/',
        EmailScheduleSuccessView.as_view(),
        name='email_schedule_success',
       ),

       # retrive scheduled emails
       path('scheduled-emails/<int:org_id>/<int:user_id>/', ScheduledEmailListView.as_view(), name='scheduled_email_list'),

       # Contact section started......
       # delete contact
       path('delete-contact/<int:org_id>/<int:contact_id>/', DeleteContactView.as_view(), name='delete_contact')




]