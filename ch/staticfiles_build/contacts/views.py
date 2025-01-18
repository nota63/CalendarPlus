from django.shortcuts import render
from django.views import View 
from django.http import JsonResponse
from accounts.models import MeetingInvitationOrganization, Profile, Organization
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q
from accounts.models import MeetingOrganization
from .models import ContactsOrganization, EmailOrganization, ScheduledEmail
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.views.generic import ListView
from django.http import HttpResponseForbidden
from django.utils import timezone
from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.views.generic import CreateView
from django.utils.timezone import localtime
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count
from .models import EmailOrganization
from accounts.models import Organization
from django.contrib.auth.models import User
import json
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.shortcuts import redirect
from django.urls import reverse_lazy

# Create your views here.


# Fetch all the contacts of the logged in user
class UserMeetingContactsView(View):
    def get(self, request, org_id):
        organization = get_object_or_404(Organization, id=org_id)
        
       
        meetings = MeetingOrganization.objects.filter(
            organization=organization,
            invitee=request.user
        ).select_related('user').order_by('meeting_date', 'start_time')  
        
      
        users = set()
        for meeting in meetings:
            users.update(meeting.participants.exclude(id=request.user.id))  
        
        
        user_details = []
        for user in users:
            profile = Profile.objects.get(user=user, organization=organization)
            
            
            past_meetings = MeetingOrganization.objects.filter(
                Q(invitee=request.user) & Q(user=user) & Q(meeting_date__lt=meeting.meeting_date)
            ).order_by('-meeting_date', '-start_time')
            future_meetings = MeetingOrganization.objects.filter(
                Q(invitee=request.user) & Q(user=user) & Q(meeting_date__gt=meeting.meeting_date)
            ).order_by('meeting_date', 'start_time')
            
           
            last_meeting = past_meetings.first()
            
         
            next_meeting = future_meetings.first()
            
            
            user_details.append({
                'user': user,
                'id':user.id,
                'role': 'Admin' if profile.is_admin else 'Manager' if profile.is_manager else 'Employee',
                'organization_name': organization.name,
                'last_meeting': {
                    'date': last_meeting.meeting_date if last_meeting else None,
                    'time': f"{last_meeting.start_time} - {last_meeting.end_time}" if last_meeting else None,
                    'title': last_meeting.meeting_title if last_meeting else None
                },
                'next_meeting': {
                    'date': next_meeting.meeting_date if next_meeting else None,
                    'time': f"{next_meeting.start_time} - {next_meeting.end_time}" if next_meeting else None,
                    'title': next_meeting.meeting_title if next_meeting else None
                }
            })

        return render(request, 'contacts/user_meeting_contacts.html', {'user_details': user_details, 'organization': organization})



# Add those users in contacts 
def add_to_contacts(request, org_id, user_id):
    if request.method == 'POST':
        try:
            organization = get_object_or_404(Organization, id=org_id)
            contact_user = get_object_or_404(User, id=user_id)
            current_user = request.user

            # Fetch the current user's profile in the specified organization
            current_user_profile = Profile.objects.filter(user=current_user, organization=organization).first()

          
            if not current_user_profile:
                return JsonResponse({'error': 'You are not part of this organization'}, status=400)

           
            contact_user_profile = Profile.objects.filter(user=contact_user, organization=organization).first()

            if not contact_user_profile:
                return JsonResponse({'error': 'The contact user is not from your organization'}, status=400)

       
            if current_user == contact_user:
                return JsonResponse({'error': 'You cannot add yourself'}, status=400)

       
            if ContactsOrganization.objects.filter(organization=organization, user=current_user, contact=contact_user).exists():
                return JsonResponse({'error': 'This user is already in your contact list'}, status=400)

         
            ContactsOrganization.objects.create(organization=organization, user=current_user, contact=contact_user)

          
            subject = "You have been added to a contact list!"
            message = f"Hello {contact_user.username},\n\n{current_user.username} has added you to their contact list in the organization {organization.name}.\n\nBest Regards,\nYour Organization"
            recipient_email = contact_user.email
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])

            return JsonResponse({'success': 'Contact added successfully, and notification sent!'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': "Invalid request"}, status=400)




# Display the users contacts
class ContactsListView(ListView):
    model = ContactsOrganization
    template_name = 'contacts/contacts_list.html'  
    context_object_name = 'contacts' 

    def get_queryset(self):
    
        org_id = self.kwargs['org_id']
        current_user = self.request.user
        
     
        organization = get_object_or_404(Organization, id=org_id)

 
        current_user_profile = Profile.objects.filter(user=current_user, organization=organization).first()
        
        if not current_user_profile:
         
            return HttpResponseForbidden('Not invalid')

 
        contacts = ContactsOrganization.objects.filter(organization=organization, user=current_user)

        print("Fetched Contacts:", contacts)

        return contacts

    def get_context_data(self, **kwargs):
       
        context = super().get_context_data(**kwargs)
        org_id = self.kwargs['org_id']
        
   
        context['organization_id'] = org_id
        context['contacts'] = context['contacts']  
        
        return context

# User details view         

class UserDetailsView(View):
    def get(self, request, org_id, user_id, *args, **kwargs):
        """
        Retrieve the details of a user within a specific organization.
        """
        
        user = get_object_or_404(User, id=user_id)
        
      
        user_data = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_joined": user.date_joined.strftime('%Y-%m-%d'),
        }
        
        return JsonResponse({"success": True, "user_data": user_data})


# Filter contacts 
class FilterContactsView(View):
    def get(self, request, org_id):
        query = request.GET.get("query", "")
      
        join_date = request.GET.get("join_date", "")

        contacts = ContactsOrganization.objects.filter(user=request.user,organization_id=org_id)

       
        if query:
            contacts = contacts.filter(
                Q(contact__username__icontains=query) |
                Q(contact__email__icontains=query)
            )

            print('Contacts found:', contacts)

        # Apply join date filter
        if join_date:
            contacts = contacts.filter(contact__date_joined=join_date)

        contacts_data = [
            {"id": c.contact.id, "username": c.contact.username, "email": c.contact.email,}

           
            for c in contacts
        ]
        return JsonResponse({"success": True, "contacts": contacts_data})

       

    def get_role(self, contact):
        """Helper method to get the role of the contact."""
        if contact.contact.profile.is_admin:
            return 'Admin'
        elif contact.contact.profile.is_manager:
            return 'Manager'
        elif contact.contact.profile.is_employee:
            return 'Employee'
        return 'Unknown'
    


# Send email view 


# Send Emails
class SendEmailView(View):
    def get(self, request, org_id, user_id):
     
        organization = Organization.objects.get(id=org_id)
        recipient = User.objects.get(id=user_id)
        return render(request, "email/send_email_form.html", {
            "organization": organization,
            "recipient": recipient
        })
    
    def post(self, request, org_id, user_id):
       
        organization = Organization.objects.get(id=org_id)
        recipient = User.objects.get(id=user_id)
        sender = request.user
        message = request.POST.get("message")

       
        profile = sender.profiles.filter(organization=organization).first()
        role = "Unknown"
        if profile:
            if profile.is_admin:
                role = "Admin"
            elif profile.is_manager:
                role = "Manager"
            else:
                role = "Employee"

        # Handle attachments if they exist
        attachment_1 = request.FILES.get("attachment_1")
        attachment_2 = request.FILES.get("attachment_2")
        attachment_3 = request.FILES.get("attachment_3")
        

        email = EmailOrganization.objects.create(
            organization=organization,
            sender=sender,
            participant=recipient,
            message=message,
            sent_at=timezone.now(),
            attachment_1=attachment_1,
            attachment_2=attachment_2,
            attachment_3=attachment_3
        )

    
        subject = f"Message from {sender.username} ({role}) at {organization.name}"
        body = f"""
        You have received a new message from {sender.username} ({role}) at {organization.name}.

        Message:
        {message}

        ---

        This email was sent by {sender.username}, who is a {role} in the {organization.name} organization.
        """

    
        email_message = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient.email]
        )

        if attachment_1:
            attachment_1_content = ContentFile(attachment_1.read())
            email_message.attach(attachment_1.name, attachment_1_content.read(), attachment_1.content_type)
        if attachment_2:
            attachment_2_content = ContentFile(attachment_2.read())
            email_message.attach(attachment_2.name, attachment_2_content.read(), attachment_2.content_type)
        if attachment_3:
            attachment_3_content = ContentFile(attachment_3.read())
            email_message.attach(attachment_3.name, attachment_3_content.read(), attachment_3.content_type)

        
        email_message.send()

   
        return JsonResponse({'suceess':'Email sent successfully'})  
 

# Retrive Emails 
class FetchEmailsView(View):
    def get(self, request, org_id, user_id):
        try:
            organization = Organization.objects.get(id=org_id)
            user = User.objects.get(id=user_id)
        except Organization.DoesNotExist or User.DoesNotExist:
         
            return render(request, 'email/emails_list.html', {
                'error_message': 'Organization or User not found.'
            })
        
        emails = EmailOrganization.objects.filter(participant=user, sender=request.user,organization=organization)

      
        return render(request, 'email/emails_list.html', {
            'organization': organization,
            'user': user,
            'emails': emails,
        
        })
    


# Email details 

class EmailDetailView(View):
    def get(self, request, org_id, user_id, email_id):
        try:
            organization = get_object_or_404(Organization, id=org_id)
            user = get_object_or_404(User, id=user_id)
            
       
            email = get_object_or_404(EmailOrganization, id=email_id, organization=organization, participant=user)
            
        
            email_data = {
                'id':email.id,
                "sender": email.sender.username,
                "participant": email.participant.username,
                "message": email.message,
                "sent_at": email.sent_at.strftime("%Y-%m-%d %H:%M:%S"),
                'status':email.status
               
            }
            return JsonResponse({"success": True, "email": email_data})
        
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})



# Download email content

def download_email_pdf(request, org_id, user_id, email_id):
    try:
       
        email = EmailOrganization.objects.get(
            id=email_id, organization_id=org_id, participant_id=user_id
        )

  
        context = {
            "organization_name": email.organization.name,
            "sender_name": email.sender.username,
            "recipient_name": email.participant.username,
            "sent_at": email.sent_at.strftime("%Y-%m-%d %H:%M"),
            "message": email.message,
            'status':email.status,
        }

     
        html_content = render_to_string("email/email_pdf_template.html", context)

     
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="email_{email_id}.pdf"'

      
        pisa_status = pisa.CreatePDF(html_content, dest=response)

     
        if pisa_status.err:
            return HttpResponse("Error generating PDF", status=500)

        return response

    except EmailOrganization.DoesNotExist:
        return HttpResponse("Email not found.", status=404)




# Email Delete
def delete_email(request, org_id, user_id, email_id):
    
    organization = get_object_or_404(Organization, id=org_id)
    user = get_object_or_404(User, id=user_id)

    
    email = EmailOrganization.objects.filter(organization=organization, participant=user, id=email_id).first()

    if email:
     
        email.delete()
        return JsonResponse({'success': True, 'message': 'Email deleted successfully.'})
    else:
    
        return JsonResponse({'success': False, 'message': 'No matching email found to delete.'})
    



# Email analytics 

def email_analysis_view(request, org_id, user_id, email_id):
    # Get the organization and email details
    organization = get_object_or_404(Organization, id=org_id)
    email = get_object_or_404(EmailOrganization, id=email_id, organization=organization,participant=user_id)
    


    emails = EmailOrganization.objects.filter(organization=organization)
    response_times = []
    labels = []
    for e in emails:
        response_time = timezone.now() - e.sent_at
        labels.append(e.sent_at.strftime('%Y-%m-%d %H:%M:%S'))  
        response_times.append(response_time.days * 24 * 60 + response_time.seconds // 60) 

    
    status_counts = {
        'Delivered': EmailOrganization.objects.filter(organization=organization, status='Delivered').count(),
        'Pending': EmailOrganization.objects.filter(organization=organization, status='Pending').count(),
        'Shipped': EmailOrganization.objects.filter(organization=organization, status='Shipped').count(),
        'Canceled': EmailOrganization.objects.filter(organization=organization, status='Canceled').count(),
    }

    
    sent_count = EmailOrganization.objects.filter(sender=email.sender, organization=organization).count()
    received_count = EmailOrganization.objects.filter(participant=email.participant, organization=organization).count()

    email_counts_per_day = EmailOrganization.objects.filter(organization=organization).extra(select={'date_sent': 'date(sent_at)'}).values('date_sent').annotate(count=Count('id'))

  
    top_senders = EmailOrganization.objects.filter(organization=organization).values('sender').annotate(sent_count=Count('sender')).order_by('-sent_count')[:5]
    top_receivers = EmailOrganization.objects.filter(organization=organization).values('participant').annotate(received_count=Count('participant')).order_by('-received_count')[:5]

  
   
    chart_data = {
        'response_times': response_times,
        'labels': labels,
        'status_counts': status_counts,
        'sent_count': sent_count,
        'received_count': received_count,
        'email_counts_per_day': list(email_counts_per_day),
        'top_senders': list(top_senders),
        'top_receivers': list(top_receivers),

    }

 
    serialized_chart_data = json.dumps(chart_data)

    return render(request, 'email/email_analysis.html', {'chart_data': serialized_chart_data,'organization':organization})



# Edit and resend Email

class EditAndResendEmailView(UpdateView):
    model = EmailOrganization

    fields = ['message']
    template_name = 'email/edit_resend_email.html'

    def get_object(self):
        org_id = self.kwargs['org_id']
        user_id = self.kwargs['user_id']
        email_id = self.kwargs['email_id']

        return EmailOrganization.objects.get(id=email_id, organization_id=org_id, participant_id=user_id)
    
    def form_valid(self, form):
        email=form.save(commit=False)
        email.sent_at = timezone.now()

        email.status= 'Delivered'
        email.save()
        self.send_resend_email(email)
        return super().form_valid(form)
    
    def send_resend_email(self, email):

        send_mail(
            subject='Re',
            message=email.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email.participant.email],
            fail_silently=False
        )

    def get_success_url(self):
        return reverse_lazy('fetch_emails',kwargs={'org_id':self.kwargs['org_id'], 'user_id':self.kwargs['user_id']})
        
    
# Schedule an Email task

class ScheduleEmailView(CreateView):
    model = ScheduledEmail
    template_name ='schedule/schedule_email.html'
    fields=['message', 'schedule_time', 'template_style']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = get_object_or_404(Organization, id=self.kwargs['org_id'])
        context['participant'] = get_object_or_404(User, id=self.kwargs['user_id'])
        return context
    
    def form_valid(self, form):
        org = get_object_or_404(Organization, id=self.kwargs['org_id'])
        participant = get_object_or_404(User, id=self.kwargs['user_id'])

        form.instance.organization = org
        form.instance.sender = self.request.user
        form.instance.participant = participant
        return super().form_valid(form)
    
    def get_success_url(self):
   
        org = get_object_or_404(Organization, id=self.kwargs['org_id'])
        participant = get_object_or_404(User, id=self.kwargs['user_id'])

     
        organization_name = org.name
        participant_name = participant.username
        message = self.object.message  
        schedule_time = self.object.schedule_time 
        template_style = self.object.template_style  

        
        return reverse_lazy(
            'email_schedule_success',
            kwargs={
                'org_id':org.id,
                'participant_id':participant.id,
                'organization_name': organization_name,
                'participant_name': participant_name,
                'message': message,
                'schedule_time': schedule_time, 
                'template_style': template_style
            }
        )

# EmailSchedule success view
class EmailScheduleSuccessView(View):
    def get(self, request, *args, **kwargs):
        organization_id = kwargs.get('org_id')
        org = get_object_or_404(Organization, id=organization_id)
        participant_id = kwargs.get('participant_id')
        organization_name = kwargs.get('organization_name')
        participant_name = kwargs.get('participant_name')
        message = kwargs.get('message')
        schedule_time = kwargs.get('schedule_time')
        template_style = kwargs.get('template_style')

        
        context = {
            'participant_id':participant_id,
            'organization':org,
            "organization_name": organization_name,
            "participant_name": participant_name,
            "message": message,
            "schedule_time": schedule_time,
            "template_style": template_style,
        }

        return render(request, 'schedule/success.html',context)
    
# Retrive scheduled emails

class ScheduledEmailListView(ListView):
    model = ScheduledEmail
    template_name = 'schedule/scheduled_email_list.html'
    context_object_name = 'scheduled_emails'
    paginate_by = 10  

    def get_queryset(self):
        org_id = self.kwargs['org_id']
        user_id = self.kwargs['user_id']
        return ScheduledEmail.objects.filter(organization_id=org_id, participant_id=user_id).order_by('-schedule_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = self.kwargs['org_id']
        context['participant'] = self.kwargs['user_id']
        return context

# --------------------------------------------------------------------------------------------------------------------------------

# Contacts section -
#    REMAIND CONTATCS OPERATION STARTS FROM HERE 


"""This view handle deletion of contacts"""

class DeleteContactView(View):
    def post(self, request, org_id, contact_id):
        try:
            # Fetch the contact object with the given parameters
            contact = get_object_or_404(
                ContactsOrganization, 
                organization_id=org_id, 
                user=request.user,  
                contact_id=contact_id
            )
            
            # Delete the contact
            contact.delete()
            return JsonResponse({'success':'True'}, status=200)
        except ContactsOrganization.DoesNotExist:
            return JsonResponse({"error": "Contact not found or you do not have permission to delete it."}, status=404)











