from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import Organization, Profile
from .models import (
    Channel, Message, Link , ActivityChannel, ChannelAccess,RetentionPolicy, RecurringMessage,RecurrenceHistory,AbusedMessage,
    ChannelEvents,Permission,AlertNotification)

from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .forms import ChannelTypeForm, ChannelNameForm, ChannelVisibilityForm
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Count
from django.views import View
from .models import Channel
from accounts.models import Profile, Organization
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse,StreamingHttpResponse
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from io import BytesIO
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from .models import Ban
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from django.core.files.storage import FileSystemStorage
from django.utils.timezone import localtime


# Create your views here.

# Create the channel 



@login_required
def create_channel(request, org_id):
    """
    Create a new channel for an organization.
    """
  
    organization = get_object_or_404(Organization, id=org_id)


    if not Profile.objects.filter(user=request.user, organization=organization, is_admin=True).exists():
        messages.error(request, "You must be an admin to create a channel.")
        return redirect('organization_dashboard', org_id=org_id)

    if request.method == 'POST':
        # Get the data from the POST request
        channel_type = request.POST.get('channel_type')
        channel_name = request.POST.get('channel_name')
        visibility = request.POST.get('visibility')
        allowed_members_ids = request.POST.getlist('allowed_members')  

        # Debugging
        print(f"Channel Type: {channel_type}")
        print(f"Channel Name: {channel_name}")
        print(f"Visibility: {visibility}")


        if not channel_name or not channel_type or not visibility:
            messages.error(request, "All fields are required.")
            return render(request, 'channels/creation/create_channel.html', {'organization': organization})

  
        channel = Channel.objects.create(
            organization=organization,
            created_by=request.user,
            name=channel_name,
            type=channel_type,
            visibility=visibility,
        )

     
        if visibility == 'PRIVATE':
            users = User.objects.filter(id__in=allowed_members_ids) 
            channel.allowed_members.set(users)


   
            subject = f"You've been added to a channel in {organization.name}"
            for user in users:
                html_message = render_to_string('channels/creation/channels_invitation.html', {
                    'user': user,
                    'channel_name': channel_name,
                    'organization': organization,
                    'domain': 'https:www.calendarPlus.com',
                    'admin_name': request.user.username,
                })
                send_mail(
                    subject=subject,
                    message=f'New notification from {organization.name}',
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )


       
        if channel_type == 'BLANK':
           
            pass

      
        messages.success(request, f"Channel '{channel_name}' has been successfully created.")
        return redirect('create_channel', org_id=org_id)


    members = Profile.objects.filter(organization=organization)
    return render(request, 'channels/creation/create_channel.html', {'organization': organization, 'members': members})


# Channel statistics 
@login_required
def channel_statistics(request, org_id):
    """
    Calculate the percentage of each channel type created and provide additional details.
    """
    organization = get_object_or_404(Organization, id=org_id)
    total_channels = Channel.objects.filter(organization=organization).count()

    # Fetch channel data
    channel_data = (
        Channel.objects.filter(organization=organization)
        .values('type')
        .annotate(count=Count('id'))
    )


    percentages = {}
    for code, name in Channel.CHANNEL_TYPES:
        channel_count = next((item['count'] for item in channel_data if item['type'] == code), 0)
        percentages[code] = {
            'channel_type': name,
            'count': channel_count,
            'percentage': round((channel_count / total_channels) * 100, 2) if total_channels > 0 else 0,
        }

    # Additional details
    last_created_channel = Channel.objects.filter(organization=organization).order_by('-created_at').first()
    most_popular_channel = max(percentages.values(), key=lambda x: x['count'], default=None)

    response = {
        'total_channels': total_channels,
        'percentages': percentages,
        'last_created': {
            'name': last_created_channel.name if last_created_channel else None,
            'type': last_created_channel.get_type_display() if last_created_channel else None,
        } if last_created_channel else None,
        'most_popular': most_popular_channel,
    }

    return JsonResponse(response)



# Display channels 
class ChannelListView(LoginRequiredMixin, View):
    template_name = 'channels/creation/channels_list.html'

    def get(self, request, org_id):
        organization = get_object_or_404(Organization, id=org_id)

        profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not profile:
            return render(request, 'error.html', {'message': 'You are not part of this organization.'})

        query = request.GET.get('q', '')

        
        public_channels = Channel.objects.filter(organization=organization, visibility='PUBLIC')
        private_channels = Channel.objects.filter(
            organization=organization, visibility='PRIVATE', allowed_members=request.user
        )
        channels = public_channels | private_channels

        # Fetch channels granted to the organization through access
        granted_channels = Channel.objects.filter(
            accesses__granted_to_organization=organization
        )

        
        channels = channels | granted_channels

        user_profile=Profile.objects.filter(organization=organization,user=request.user).first()

      
        if query:
            channels = channels.filter(Q(name__icontains=query) | Q(type__icontains=query))

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            channel_data = [
                {
                    'name': channel.name,
                    'type': channel.get_type_display(),
                    'visibility': channel.get_visibility_display(),
                    'created_at': channel.created_at.strftime('%B %d, %Y'),
                    'granted_to_org': channel.accesses.first().granted_to_organization.name if channel.accesses.exists() else None,  # Fetch granted organization
                }
                for channel in channels.distinct()
            ]
            return JsonResponse({'channels': channel_data})

        context = {
            'organization': organization,
            'channels': channels.distinct(),
            'user_profile':user_profile,
        }
        return render(request, self.template_name, context)






# Redirect to channel room
def channel_chat(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id)

    
    pinned_messages = Message.objects.filter(channel=channel, is_pinned=True).order_by('-timestamp')
    unpinned_messages = Message.objects.filter(channel=channel, is_pinned=False).order_by('timestamp')


    messages = list(pinned_messages) + list(unpinned_messages)

    links = Link.objects.filter(channel=channel).order_by('timestamp')


    ban_entry = Ban.objects.filter(
        user=request.user,
        channel=channel,
        organization=channel.organization,
    ).first()

    if ban_entry and (ban_entry.end_time is None or ban_entry.end_time > now()):
        return HttpResponseForbidden("You are banned from accessing this channel.")

    return render(request, 'channels/rooms/channel_chat.html', {'channel': channel, 'messages': messages, 'links': links})




# Get organization members to mention

def get_organization_members(request,organization_id):
    organization = get_object_or_404(Organization, id=organization_id)


 
    members = Profile.objects.filter(organization=organization)
   

   
    members_data = [
        {
            'id': member.user.id,
            'username': member.user.username,
            'full_name': f"{member.user.first_name} {member.user.last_name}"  
        }
        for member in members
    ]
    return JsonResponse({'members': members_data})


# Get channel members
def get_channel_members(request, org_id, channel_id):

    organization = get_object_or_404(Organization, id=org_id)




    user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
    if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
        return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)


    channel = get_object_or_404(Channel, id=channel_id, organization=organization)

    if channel.visibility == 'PUBLIC':
        members = Profile.objects.filter(organization=organization)
    else:
        
        members = channel.allowed_members.all()

   
    member_list = [{"id": member.user.id, "username": member.user.username} for member in members]
    print("MEMBERS FOUND:", member_list)

    return JsonResponse({'members': member_list})


# Fetch activity logs
def fetch_activity_logs(request, channel_id, org_id):
    organization = get_object_or_404(Organization, id=org_id)
    channel = get_object_or_404(Channel, id=channel_id, organization=organization)

    user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
    if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
        return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)

    # Fetch the latest activity logs for the channel
    activity_logs = ActivityChannel.objects.filter(channel=channel).order_by('-timestamp')

    logs = []
    for log in activity_logs:
        logs.append({
            'user': log.user.username,
            'content': log.content,
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),  
        })

    return JsonResponse({'success': True, 'logs': logs})



# Implement search bar 

def search_messages_links(request, org_id, channel_id):
    organization=get_object_or_404(Organization, id=org_id)
    user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
    if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
        return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)

    query = request.GET.get('q', '')  
    if not query:
        return JsonResponse({'messages': [], 'links': []}) 

   
    messages = Message.objects.filter(
        Q(content__icontains=query) | Q(audio__icontains=query) | Q(video__icontains=query),
        channel_id=channel_id,
        organization_id=org_id
    ).values('user__username', 'content', 'timestamp')

    links = Link.objects.filter(
        Q(text__icontains=query) | Q(link__icontains=query),
        channel_id=channel_id,
        organization_id=org_id
    ).values('user__username', 'text', 'link', 'timestamp')

    return JsonResponse({'messages': list(messages), 'links': list(links)})


#  Get channel details

def channel_details(request, org_id, channel_id):
    organization=get_object_or_404(Organization, id=org_id)
    user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
    if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
        return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)

    channel = get_object_or_404(Channel, id=channel_id, organization_id=org_id)
    created_by = channel.created_by.username 

   
    members = Profile.objects.filter(organization_id=org_id).select_related('user')
    member_list = [{'full_name': profile.user.username} for profile in members]

 
    data = {
        'name': channel.name,
        'type': channel.get_type_display(),  
        'visibility': channel.get_visibility_display(), 
        'created_at': channel.created_at.strftime('%Y-%m-%d %H:%M'), 
        'created_by': created_by,
        'members': member_list,
    }

    return JsonResponse(data)


# Export data via email

def export_data(request, org_id, channel_id):
    try:

        organization = get_object_or_404(Organization, id=org_id)
        channel = get_object_or_404(Channel, id=channel_id, organization=organization)

        user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
        if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
            return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)

     
        messages = Message.objects.filter(channel=channel)
        links = Link.objects.filter(channel=channel)
        members = Profile.objects.filter(organization=organization)

        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="export_{organization.name}_channel_{channel.name}_data.pdf"'

    
        pdf = canvas.Canvas(response, pagesize=letter)
        width, height = letter

 
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, height - 40, f"Organization: {organization.name}")
        pdf.drawString(100, height - 60, f"Channel: {channel.name}")
        pdf.drawString(100, height - 80, f"Channel Type: {channel.get_type_display()}")
        pdf.drawString(100, height - 100, f"Visibility: {channel.get_visibility_display()}")
        pdf.drawString(100, height - 120, f"Created At: {channel.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        pdf.drawString(100, height - 140, f"Created By: {channel.created_by.username}")

   
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, height - 180, "Messages:")
        y_position = height - 200
        pdf.setFont("Helvetica", 10)
        for message in messages:
            pdf.drawString(100, y_position, f"{message.user.username}: {message.content[:80]}...")  # Display first 80 characters of message
            y_position -= 20
            if y_position < 100:
                pdf.showPage()  
                y_position = height - 40


        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, y_position, "Links:")
        y_position -= 20
        pdf.setFont("Helvetica", 10)
        for link in links:
            pdf.drawString(100, y_position, f"{link.text}: {link.link}")  
            y_position -= 20
            if y_position < 100:
                pdf.showPage()
                y_position = height - 40


        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, y_position, "Members:")
        y_position -= 20
        pdf.setFont("Helvetica", 10)
        for member in members:
            pdf.drawString(100, y_position, f"{member.user.username}")
            y_position -= 20
            if y_position < 100:
                pdf.showPage()
                y_position = height - 40

        pdf.save()


        send_email_with_attachment(request.user.email, response)

        current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

        activity = ActivityChannel.objects.create(
          user=request.user,
          channel=channel,
          organization=organization,
          action_type="DATA_EXPORT",
          content=f'The channel contents were exported by {request.user} at {current_time}.'
        )

        return response

    except Exception as e:
        print(f'Error exporting data: {e}')
        return HttpResponse('Error exporting data', status=500)

def send_email_with_attachment(to_email, pdf_file):
    subject = "Exported Data: Organization & Channel Details"
    message = "Please find attached the exported data for the organization and channel."
    from_email = settings.DEFAULT_FROM_EMAIL

   
    pdf_buffer = BytesIO(pdf_file.content)
    

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email,
        to=[to_email]
    )
    

    email.attach('exported_data.pdf', pdf_buffer.read(), 'application/pdf')
    

    email.send(fail_silently=False)


# Channel statistics 

def channel_statistics(request, org_id, channel_id):
    try:
        organization = get_object_or_404(Organization, id=org_id)
        channel = get_object_or_404(Channel, id=channel_id, organization=organization)

        user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
        if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
           return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)

      
        total_messages = Message.objects.filter(channel=channel).count()

        user_message_counts = Message.objects.filter(channel=channel) \
            .values('user') \
            .annotate(message_count=Count('id')) \
            .order_by('-message_count')

    
        total_links = Link.objects.filter(channel=channel).count()

       
        user_link_counts = Link.objects.filter(channel=channel) \
            .values('user') \
            .annotate(link_count=Count('id')) \
            .order_by('-link_count')

        
        combined_user_stats = (
            Message.objects.filter(channel=channel)
            .values('user')
            .annotate(message_count=Count('id'))
        ).values('user', 'message_count')
        
        link_stats = (
            Link.objects.filter(channel=channel)
            .values('user')
            .annotate(link_count=Count('id'))
        ).values('user', 'link_count')

      
        combined_stats = {}
        for stat in combined_user_stats:
            combined_stats[stat['user']] = stat['message_count']

        for stat in link_stats:
            if stat['user'] in combined_stats:
                combined_stats[stat['user']] += stat['link_count']
            else:
                combined_stats[stat['user']] = stat['link_count']

       
        king_user_id = max(combined_stats, key=combined_stats.get)
        king_user = get_object_or_404(User, id=king_user_id)

    
        user_message_labels = [str(user['user']) for user in user_message_counts]  
        user_message_data = [user['message_count'] for user in user_message_counts]

        user_link_labels = [str(user['user']) for user in user_link_counts] 
        user_link_data = [user['link_count'] for user in user_link_counts]

  
        message_chart = {
            'labels': user_message_labels,
            'data': user_message_data,
            'label': 'Messages Sent by Users',
            'background_color': 'rgba(75, 192, 192, 0.2)',
            'border_color': 'rgba(75, 192, 192, 1)',
            'border_width': 1
        }

        link_chart = {
            'labels': user_link_labels,
            'data': user_link_data,
            'label': 'Links Shared by Users',
            'background_color': 'rgba(153, 102, 255, 0.2)',
            'border_color': 'rgba(153, 102, 255, 1)',
            'border_width': 1
        }

        
        response_data = {
            'total_messages': total_messages,
            'total_links': total_links,
            'user_message_counts': [{'user': user['user'], 'message_count': user['message_count']} for user in user_message_counts],
            'user_link_counts': [{'user': user['user'], 'link_count': user['link_count']} for user in user_link_counts],
            'king_user': king_user.username,
            'message_chart': message_chart,
            'link_chart': link_chart,
        }

        activity = ActivityChannel.objects.create(
          user=request.user,
          channel=channel,
          organization=organization,
          action_type="EXPLORE_STATISTICS",
          content=f'{request.user} viewed channel statistics'
        )

        return JsonResponse(response_data)

    except Exception as e:
        print(f"Error fetching statistics: {e}")
        return JsonResponse({'error': 'Unable to fetch statistics'}, status=500)



# Filter messages & links 
@login_required
def filter_messages(request, org_id, channel_id):
    organization=get_object_or_404(Organization, id=org_id)
    user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
    if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
        return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)

    filter_option = request.GET.get('filter_option')
    specific_date = request.GET.get('specific_date') 
    

    now = timezone.now()

    # Filter the messages based on the filter option
    if filter_option == 'today':
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        messages = Message.objects.filter(channel_id=channel_id, timestamp__gte=start_of_day)
        links = Link.objects.filter(channel_id=channel_id, timestamp__gte=start_of_day)
    
    elif filter_option == 'yesterday':
        start_of_day = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        messages = Message.objects.filter(channel_id=channel_id, timestamp__gte=start_of_day, timestamp__lt=end_of_day)
        links = Link.objects.filter(channel_id=channel_id, timestamp__gte=start_of_day, timestamp__lt=end_of_day)

    elif filter_option == 'last_week':
        start_of_week = now - timedelta(days=now.weekday())  
        end_of_week = start_of_week + timedelta(days=7) 
        messages = Message.objects.filter(channel_id=channel_id, timestamp__gte=start_of_week, timestamp__lt=end_of_week)
        links = Link.objects.filter(channel_id=channel_id, timestamp__gte=start_of_week, timestamp__lt=end_of_week)

    elif filter_option == 'last_month':
        start_of_month = now.replace(day=1) 
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1)  
        messages = Message.objects.filter(channel_id=channel_id, timestamp__gte=start_of_month, timestamp__lt=end_of_month)
        links = Link.objects.filter(channel_id=channel_id, timestamp__gte=start_of_month, timestamp__lt=end_of_month)

    elif filter_option == 'specific_date' and specific_date:
        specific_date_obj = timezone.datetime.strptime(specific_date, '%Y-%m-%d').date()
        messages = Message.objects.filter(channel_id=channel_id, timestamp__date=specific_date_obj)
        links = Link.objects.filter(channel_id=channel_id, timestamp__date=specific_date_obj)

    else:
   
        messages = Message.objects.filter(channel_id=channel_id)
        links = Link.objects.filter(channel_id=channel_id)

 
    response_data = {
        'messages': [
            {
                'user': message.user.username,
                'content': message.content,
                'timestamp': message.timestamp.strftime('%H:%M'),
            
            }
            for message in messages
        ],
        'links': [
            {
                'user': link.user.username,
                'text': link.text,
                'timestamp': link.timestamp.strftime('%H:%M'),
                'link': link.link,
            }
            for link in links
        ],
    }

    return JsonResponse(response_data)

# Delete users messages 
@csrf_exempt 
def delete_user_messages(request, org_id, channel_id):
    organization=get_object_or_404(Organization,id=org_id)
    channel=get_object_or_404(Channel,id=channel_id,organization=organization)

    user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
    if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
        return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)


    if request.method == 'POST':
        try:
      
            body = json.loads(request.body)
            password = body.get('password')

        
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'message': 'User not authenticated.'}, status=403)

            user = request.user
            if not check_password(password, user.password):
                return JsonResponse({'success': False, 'message': 'Incorrect password.'}, status=403)

            
            Message.objects.filter(user=user, channel_id=channel_id, organization_id=org_id).delete()
            Link.objects.filter(user=user, channel_id=channel_id, organization_id=org_id).delete()
            activity = ActivityChannel.objects.create(
                user=user,
                channel=channel,
                organization=organization,
                action_type="MESSAGES_DELETE",
                content=f'{user} deleted his messages'
            )

            return JsonResponse({'success': True, 'message': 'All your messages have been deleted successfully.'})
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)




# Delete messages or links

def delete_message(request, org_id, channel_id, message_id):
    if request.method == 'POST':
        organization = get_object_or_404(Organization, id=org_id)
        channel = get_object_or_404(Channel, id=channel_id, organization=organization)

        user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
        if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
           return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)


   
        message = Message.objects.filter(id=message_id, channel=channel, organization=organization, user=request.user).first()

        if message:
            message.delete()
            messages.success(request, "Message deleted successfully")
          
            activity = ActivityChannel.objects.create(
               user=request.user,
               channel=channel,
               organization=organization,
               action_type="MESSAGE_DELETE",
               content=f'{request.user} deleted his message {message.content}'
             )

        else:
            messages.error(request, "Message not found or you do not have permission to delete it.")
        
        return redirect('channel_chat', channel_id=channel.id)  
    else:
        return JsonResponse({'success': False, 'error': 'Invalid method. Only POST is allowed.'})
    


# Delete link    

def delete_link(request, org_id, channel_id, link_id):
    if request.method == 'POST':
        organization = get_object_or_404(Organization, id=org_id)
        channel = get_object_or_404(Channel, id=channel_id, organization=organization)

        user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
        if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
           return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)


   
        link = Link.objects.filter(id=link_id, channel=channel, organization=organization, user=request.user).first()

        if link:
            link.delete()
            messages.success(request, "Message deleted successfully")
          
            activity = ActivityChannel.objects.create(
               user=request.user,
               channel=channel,
               organization=organization,
               action_type="LINK_DELETE",
               content=f'{request.user} deleted his link {link.link} wrapped text {link.text}'
             )

        else:
            messages.error(request, "Link not found or you do not have permission to delete it.")
        
        return redirect('channel_chat', channel_id=channel.id)  
    else:
        return JsonResponse({'success': False, 'error': 'Invalid method. Only POST is allowed.'})
    


# Edit message 
import logging

logger = logging.getLogger(__name__)

def edit_message(request, org_id, channel_id, message_id):
    if request.method == 'POST':
        try:
       
            logger.debug(f"Received request body: {request.body}")

  
            data = json.loads(request.body)
            content = data.get('content')

        
            logger.debug(f"Received content: {content}")

       
            if not content or content.strip() == '':
                logger.warning("Message content is empty or only spaces.")
                return JsonResponse({'success': False, 'error': 'Message content cannot be empty.'})

            organization = get_object_or_404(Organization, id=org_id)
            logger.debug(f"Found organization: {organization.name} (ID: {organization.id})")

            channel = get_object_or_404(Channel, id=channel_id, organization=organization)
            logger.debug(f"Found channel: {channel.name} (ID: {channel.id})")
            user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
            if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
              return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)


     
            message = get_object_or_404(Message, id=message_id, channel=channel, user=request.user)
            logger.debug(f"Found message to edit: {message.content} (ID: {message.id})")

            message.content = content
            message.save()
            logger.info(f"Message successfully updated: {message.content} (ID: {message.id})")

            activity = ActivityChannel.objects.create(
               user=request.user,
               channel=channel,
                organization=organization,
                action_type="MESSAGE_EDITED",
               content=f'{request.user} Edited the message and new message is {content}'
            )


            return JsonResponse({'success': True, 'message': 'Message updated successfully.'})

        except Exception as e:
            logger.error(f"Error occurred while processing the request: {e}")
            return JsonResponse({'success': False, 'error': f'An error occurred: {str(e)}'})

    else:
        logger.warning(f"Invalid method: {request.method}. Only POST is allowed.")
        return JsonResponse({'success': False, 'error': 'Invalid method. Only POST is allowed.'})
    

# Edit the link 

logger = logging.getLogger(__name__)

def edit_link(request, org_id, channel_id, link_id):
    if request.method == 'POST':
        try:
            logger.debug(f"Received request body: {request.body}")
            data = json.loads(request.body)
            text = data.get('text')
            link_url = data.get('link')

            logger.debug(f"Received link text: {text} and link URL: {link_url}")

            if not text or not link_url:
                logger.warning("Link text or URL is empty.")
                return JsonResponse({'success': False, 'error': 'Both link text and URL are required.'})

            organization = get_object_or_404(Organization, id=org_id)
            logger.debug(f"Found organization: {organization.name} (ID: {organization.id})")
            channel = get_object_or_404(Channel, id=channel_id, organization=organization)
            logger.debug(f"Found channel: {channel.name} (ID: {channel.id})")

          
            user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
            if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
              return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)


            link_obj = get_object_or_404(Link, id=link_id, channel=channel, organization=organization, user=request.user)
            logger.debug(f"Found link to edit: {link_obj.text} (ID: {link_obj.id})")

            link_obj.text = text
            link_obj.link = link_url
            link_obj.save()
            logger.info(f"Link successfully updated: {link_obj.text} (ID: {link_obj.id})")

            
            activity = ActivityChannel.objects.create(
                user=request.user,
                channel=channel,
                organization=organization,
                action_type="LINK_EDITED",
                content=f'{request.user} edited the link: {text}'
            )

            return JsonResponse({'success': True, 'message': 'Link updated successfully.'})

        except Exception as e:
            logger.error(f"Error occurred while processing the request: {e}")
            return JsonResponse({'success': False, 'error': f'An error occurred: {str(e)}'})

    else:
        logger.warning(f"Invalid method: {request.method}. Only POST is allowed.")
        return JsonResponse({'success': False, 'error': 'Invalid method. Only POST is allowed.'})



# Calculate memory usages of messages and links

def calculate_memory_usage_file(file_field):
    """Helper to calculate memory usage of file."""
    if file_field and file_field.name:
        try:
            return file_field.size
        except Exception:
            return 0
    return 0


def calculate_memory_usage_text(text):
    """Helper to calculate memory usage of text."""
    return len(text.encode('utf-8')) if text else 0


def get_channel_data(request, org_id, channel_id):
    """Fetch all relevant statistics for a channel."""

    organization=get_object_or_404(Organization, id=org_id)
    user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
    if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
        return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)

    try:
      
        if not org_id or not channel_id:
            return JsonResponse({"error": "org_id and channel_id are required."}, status=400)

      
        messages = Message.objects.filter(user=request.user,channel_id=channel_id, organization_id=org_id)
        links = Link.objects.filter(user=request.user,channel_id=channel_id, organization_id=org_id)

        total_messages_count = messages.count()
        total_links_count = links.count()

       
        total_text_memory = sum(calculate_memory_usage_text(msg.content) for msg in messages)
        total_audio_memory = sum(calculate_memory_usage_file(msg.audio) for msg in messages)
        total_video_memory = sum(calculate_memory_usage_file(msg.video) for msg in messages)
        total_links_text_memory = sum(calculate_memory_usage_text(link.text) for link in links)
        total_links_memory = sum(calculate_memory_usage_text(link.link) for link in links)

  
        total_message_memory = total_text_memory + total_audio_memory + total_video_memory
        total_links_memory_combined = total_links_text_memory + total_links_memory
        total_memory = total_message_memory + total_links_memory_combined

 
        response_data = {
            "total_messages_count": total_messages_count,
            "total_links_count": total_links_count,
            "total_text_memory": total_text_memory, 
            "total_audio_memory": total_audio_memory, 
            "total_video_memory": total_video_memory, 
            "total_links_text_memory": total_links_text_memory, 
            "total_links_memory": total_links_memory, 
            "total_message_memory": total_message_memory, 
            "total_links_memory_combined": total_links_memory_combined, 
            "total_memory": total_memory,  
        }

        return JsonResponse(response_data, status=200)

    except Exception as e:
        print(f"Error fetching channel data: {e}")
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)


# FILTER MESSAGES AND LINKS BASED ON USER 

# FETCH USERS

@csrf_exempt
def fetch_users(request, org_id, channel_id):
    organization = get_object_or_404(Organization, id=org_id)

    user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
    if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
        return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)


    channel = get_object_or_404(Channel, id=channel_id, organization=organization)

  
    if channel.visibility == 'PUBLIC':
        members = Profile.objects.filter(organization=organization)
    else:
        members = channel.allowed_members.all()

 
    user_list = [{"id": member.user.id, "username": member.user.username} for member in members]
    print("USERS FOUND:", user_list)

    
    return JsonResponse({'users': user_list, 'channel_name': channel.name})


# Filter messages and links based on user

def filter_by_user(request, org_id, channel_id, user_id):
    if request.method == "GET":
        
        organization = get_object_or_404(Organization, id=org_id)
        user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
        if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
          return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)

        channel = get_object_or_404(Channel, id=channel_id, organization=organization)
        user = get_object_or_404(User, id=user_id)

        activity = ActivityChannel.objects.create(
          user=user,
          channel=channel,
          organization=organization,
          action_type="FILTERED_MESSAGES",
          content=F'{request.user} filtered the messages of {user.username}'
    )

        
      
        messages = Message.objects.filter(
            organization=organization,
            channel=channel,
            user=user
        ).order_by('-timestamp')
        
        links = Link.objects.filter(
            organization=organization,
            channel=channel,
            user=user
        ).order_by('-timestamp')
        
   
        messages_data = [
            {
                "id": message.id,
                'user':user.username,
                "content": message.content,
                "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "audio": message.audio.url if message.audio else None,
                "video": message.video.url if message.video else None,
            }
            for message in messages
        ]
        
        links_data = [
            {
                "id": link.id,
                'user':user.username,
                "text": link.text,
                "link": link.link,
                "timestamp": link.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for link in links
        ]

        return JsonResponse({"messages": messages_data, "links": links_data}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)



# DELETE ALL CHANNEL DATA (ONLY ADMIN)


@login_required
@csrf_exempt
def delete_channel_data(request, org_id, channel_id):
    if request.method == "POST":
     
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

  
        organization = get_object_or_404(Organization, id=org_id)
        channel = get_object_or_404(Channel, id=channel_id, organization=organization)

        user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
        if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
          return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)


  
        if channel.created_by != request.user:
            return JsonResponse({'error': 'You are not authorized to delete data for this channel.'}, status=403)

        # Get the password entered by the user
        password = data.get('password')
        if not password:
            return JsonResponse({'error': 'Password is required.'}, status=400)


        if not check_password(password, request.user.password):
            return JsonResponse({'error': 'Invalid password. Please try again.'}, status=400)

  
        data_to_delete = data.get('data_to_delete', [])
        if not isinstance(data_to_delete, list):
            return JsonResponse({'error': 'Invalid data to delete format.'}, status=400)

     
        if 'messages' in data_to_delete:
            Message.objects.filter(channel=channel).delete()

     
        if 'links' in data_to_delete:
            Link.objects.filter(channel=channel).delete()

     
        if 'audio' in data_to_delete:
            Message.objects.filter(channel=channel, audio__isnull=False).delete()

       
        if 'video' in data_to_delete:
            Message.objects.filter(channel=channel, video__isnull=False).delete()

    
        if 'activity' in data_to_delete:
            ActivityChannel.objects.filter(channel=channel).delete()

     
        ActivityChannel.objects.create(
            user=request.user,
            channel=channel,
            organization=organization,
            action_type="DATA_EXPORT",
            content=f"Deleted the following data: {', '.join(data_to_delete)}"
        )

        return JsonResponse({'message': 'Data deleted successfully.'})

    return JsonResponse({'error': 'Invalid request method. Only POST is allowed.'}, status=405)


# BAN USER (ADMIN ONLY)


@csrf_exempt
def ban_user(request, org_id, channel_id, user_id):
    organization = get_object_or_404(Organization, id=org_id)
    user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
    if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
        return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)

    channel = get_object_or_404(Channel, id=channel_id, organization=organization)
    user_to_ban = get_object_or_404(User, id=user_id)

    banning_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not banning_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)
    
  
    if not banning_profile.is_admin:
        return JsonResponse({'error': 'You do not have permission to ban users.'}, status=403)

    
    existing_ban = Ban.objects.filter(user=user_to_ban, channel=channel).first()

  
    ban_duration = request.POST.get('ban_duration', 'permanent')  
    reason = request.POST.get('reason', '')

  
    if ban_duration == '1 day':
        end_time = now() + timedelta(days=1)
    elif ban_duration == '1 week':
        end_time = now() + timedelta(weeks=1)
    elif ban_duration == '1 month':
        end_time = now() + timedelta(weeks=4)
    elif ban_duration == 'permanent':
        end_time = None  
    else:
        return JsonResponse({'error': 'Invalid ban duration'}, status=400)

    if existing_ban:
       
        existing_ban.reason = reason
        existing_ban.end_time = end_time
        existing_ban.save()

        return JsonResponse({'message': 'User banned successfully', 'ban_duration': ban_duration})

   
    Ban.objects.create(
        organization=organization,
        channel=channel,
        user=user_to_ban,
        banned_by=request.user,
        reason=reason,
        start_time=now(),
        end_time=end_time
    )

    ActivityChannel.objects.create(
            user=request.user,
            channel=channel,
            organization=organization,
            action_type="BAN_USER",
            content=f"{request.user} Banned {user_to_ban} from the channel"
        )


    return JsonResponse({'message': 'User banned successfully', 'ban_duration': ban_duration})


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Give channel access to other organizations

# fetch admin organizations

def fetch_admin_organizations(request, org_id, channel_id):
    """
    Fetch all organizations where the request.user is an admin, excluding those that already have access to the channel.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized access'}, status=401)

    current_org = get_object_or_404(Organization, id=org_id)
    user_profile = Profile.objects.filter(user=request.user, organization=current_org).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

    if not current_org.profiles.filter(user=request.user, is_admin=True).exists():
        return JsonResponse({'error': 'You are not an admin of this organization'}, status=403)


    admin_organizations = Organization.objects.filter(
        profiles__user=request.user,
        profiles__is_admin=True
    ).exclude(id=org_id)  

    
    organizations_with_access = ChannelAccess.objects.filter(channel_id=channel_id)
    organizations_with_access_ids = organizations_with_access.values_list('granted_to_organization', flat=True)

   
    admin_organizations = admin_organizations.exclude(id__in=organizations_with_access_ids)

    org_data = [{'id': org.id, 'name': org.name, 'description': org.description} for org in admin_organizations]
    return JsonResponse({'organizations': org_data}, status=200)




# Grant access to other organization

@csrf_exempt
def grant_channel_access(request, org_id, channel_id, selected_org_id):
    """
    Grant access of a channel to a selected organization.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized access'}, status=401)

  
    owning_org = get_object_or_404(Organization, id=org_id)
    user_profile = Profile.objects.filter(user=request.user, organization=owning_org).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

    if not owning_org.profiles.filter(user=request.user, is_admin=True).exists():
        return JsonResponse({'error': 'You are not an admin of this organization'}, status=403)

    channel = get_object_or_404(Channel, id=channel_id, organization=owning_org)

   
    selected_org = get_object_or_404(Organization, id=selected_org_id)

    if ChannelAccess.objects.filter(channel=channel, granted_to_organization=selected_org).exists():
        return JsonResponse({'error': 'Access already granted to this organization'}, status=400)

    # Grant access
    ChannelAccess.objects.create(
        channel=channel,
        owning_organization=owning_org,
        granted_to_organization=selected_org,
        granted_by=request.user
    )

    activity = ActivityChannel.objects.create(
        user=request.user,
        channel=channel,
        organization=owning_org,
        action_type="CHANNEL_ACCESS",
        content=f"{request.user} give channel accesss to other workspace {selected_org.name}"
    )

    selected_org_admin = Profile.objects.filter(organization=selected_org, is_admin=True).first()
    if selected_org_admin:
        subject = f"Channel Access Granted to {channel.name} for {selected_org.name}"
        message = f"""
        Dear {selected_org_admin.user.first_name} {selected_org_admin.user.last_name},

        We are pleased to inform you that your organization, {selected_org.name}, has been granted access to the channel "{channel.name}" in the organization "{owning_org.name}".

        Channel Details:
        - Channel Name: {channel.name}
        - Description: {channel.type}
        - Organization: {owning_org.name}

        If you have any questions or need further assistance, feel free to reach out.

        Best regards,
        {request.user.first_name} {request.user.last_name}
        {owning_org.name} Admin
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL, 
            [selected_org_admin.user.email], 
            fail_silently=False,
        )


    return JsonResponse({'success': f'Access granted to {selected_org.name}'}, status=200)



# RETENTION POLICY

@login_required
@csrf_exempt
def set_retention_policy(request, org_id, channel_id):
   
    organization = get_object_or_404(Organization, id=org_id)
    channel = get_object_or_404(Channel, id=channel_id, organization=organization)

    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

    if request.user != organization.created_by:
        return JsonResponse({'error': 'You must be the admin of the organization to set policies.'}, status=403)

    if request.method == "POST":
        try:
        
            payload = json.loads(request.body)

            retention_period = payload.get('retention_period')
            custom_days = payload.get('custom_days')

      
            retention_period = int(retention_period)
            if retention_period == 0:  
                if not custom_days:
                    return JsonResponse({'error': 'Custom days must be provided for a custom retention period.'}, status=400)
                custom_days = int(custom_days)
                if custom_days <= 0:
                    return JsonResponse({'error': 'Custom days must be a positive integer.'}, status=400)
            else:
                custom_days = None 

            
            retention_policy, created = RetentionPolicy.objects.update_or_create(
                organization=organization,
                channel=channel,
                defaults={'retention_period': retention_period, 'custom_days': custom_days, 'created_by': request.user}
            )

            activity = ActivityChannel.objects.create(
              user=request.user,
              channel=channel,
              organization=organization,
              action_type="SET_RETENTION_POLICY",
              content=f'{request.user} has set Retention Policy to {retention_period} days  {custom_days}'
           )


            return JsonResponse({'success': 'Retention policy saved successfully.'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)


# Pin message

@require_POST
@csrf_exempt
def pin_message(request, org_id, channel_id, message_id):
    """
    View to pin or unpin a message in a channel.
    """
    try:
        
        organization = get_object_or_404(Organization, id=org_id)
        user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
        if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
          return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)

      
        channel = get_object_or_404(Channel, id=channel_id, organization=organization)

        
        message = get_object_or_404(Message, id=message_id, channel=channel)

   
        message.is_pinned = not message.is_pinned
        message.save()
        activity = ActivityChannel.objects.create(
          user=request.user,
          channel=channel,
          organization=organization,
          action_type="PINNED_MESSAGE",
          content=f'{request.user} Pinned the message {message.content}',
    )


        return JsonResponse({
            "success": True,
            "message": f"Message {'pinned' if message.is_pinned else 'unpinned'} successfully.",
            "is_pinned": message.is_pinned,
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e),
        }, status=400)



# Star / Unstar message

def toggle_star_message(request, org_id, channel_id, message_id):
    
    organization = get_object_or_404(Organization, id=org_id)
    channel = get_object_or_404(Channel, id=channel_id, organization=organization)
    user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
    if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
        return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)



    message = get_object_or_404(Message, id=message_id, channel=channel,user=request.user,organization=organization)

  
    message.is_starred = not message.is_starred
    message.save()

    activity = ActivityChannel.objects.create(
          user=request.user,
          channel=channel,
          organization=organization,
          action_type="STARRED_MESSAGE",
          content=f'{request.user} Starred the message {message.content}',
    )


   
    return JsonResponse({
        'message_id': message.id,
        'is_starred': message.is_starred,
        'status': 'success',
        'message': 'Message starred' if message.is_starred else 'Message unstarred'
    })


# Handle parent replies

@csrf_exempt
def handle_reply(request, org_id, channel_id, message_id):
    if request.method == "POST":
        try:
         
            data = json.loads(request.body)
            content = data.get("content", "").strip()

            if not content:
                return JsonResponse({"error": "Reply content cannot be empty."}, status=400)

            organization = get_object_or_404(Organization, id=org_id)
            channel = get_object_or_404(Channel, id=channel_id, organization=organization)
            parent_message = get_object_or_404(Message, id=message_id, channel=channel)

            user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
            if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
               return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)


            reply = Message.objects.create(
                channel=channel,
                user=request.user,  
                content=content,
                parent=parent_message,
                organization=organization
            )

            activity = ActivityChannel.objects.create(
               user=request.user,
               channel=channel,
              organization=organization,
              action_type="MESSAGE_REPLY",
              content=f'{request.user} Replied to {parent_message.user.username} - {parent_message.content} -- {reply.parent}'

        )

            return JsonResponse({
                "message": "Reply created successfully.",
                "reply": {
                    "id": reply.id,
                    "content": reply.content,
                    "user": reply.user.username,
                    "timestamp": reply.timestamp.strftime("%H:%M"),
                    "parent_id": parent_message.id
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON body."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)


# HANDLE RECURRING MESSAGES

@csrf_exempt 
def set_recurring_message(request, org_id, channel_id, message_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid HTTP method. Use POST.'}, status=405)

    try:
        
        data = json.loads(request.body)
        recurrence_type = data.get('recurrence_type')
        recurrence_days = data.get('recurrence_days', [])
        end_date = data.get('end_date')

    
        valid_types = ['daily', 'weekly', 'monthly', 'yearly', 'custom']
        if recurrence_type not in valid_types:
            return JsonResponse({'error': 'Invalid recurrence type.'}, status=400)

 
        organization = get_object_or_404(Organization, id=org_id)
        channel = get_object_or_404(Channel, id=channel_id)
        message = get_object_or_404(Message, id=message_id)

        user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
        if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
          return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)


        if message.channel != channel or channel.organization != organization:
            return JsonResponse({'error': 'Message does not belong to the specified organization or channel.'}, status=400)

      
        recurring_message, created = RecurringMessage.objects.update_or_create(
            organization=organization,
            channel=channel,
            user=message.user,
            text=message.content,
            defaults={
                'recurrence_type': recurrence_type,
                'recurrence_days': recurrence_days,
                'end_date': end_date,
            }
        )

        activity = ActivityChannel.objects.create(
               user=request.user,
               channel=channel,
               organization=organization,
              action_type="SET_RECURRING_MESSAGE",
              content=f'{request.user} Set-up the message as recurring - {message.content}  For  {recurrence_type} -- End Date - {end_date}'

        )


        response = {
            'message': 'Recurring message set successfully.',
            'recurring_message_id': recurring_message.id,
            'status': 'created' if created else 'updated'
        }
        return JsonResponse(response, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# RECURRING MESSAGES DASHBOARD & MONITOR 

import datetime 


logger = logging.getLogger(__name__)
def monitor_recurring_messages(request, org_id, channel_id):
    """
    View to monitor recurring messages and their history.
    Displays both pending and sent recurring messages.
    """
    try:
        
        organization = get_object_or_404(Organization, id=org_id)
        channel = get_object_or_404(Channel, id=channel_id)

        user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
        if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
          return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)


       
        recurring_messages = RecurringMessage.objects.filter(
            organization=organization, channel=channel
        ).order_by('-start_date')

     
        history = RecurrenceHistory.objects.filter(
            organization=organization, channel=channel
        ).order_by('-sent_at')

     
        pending_messages = recurring_messages.filter(end_date__gte=datetime.datetime.now().date())
        sent_messages = history.filter(sent_at__lte=datetime.datetime.now()).order_by('-sent_at')


        response_data = {
            'organization': organization.name,
            'channel': channel.name,
            'pending_messages': [
                {
                    'id': message.id,
                    'text': message.text,
                    'start_date': message.start_date,
                    'end_date': message.end_date,
                    'recurrence_type': message.recurrence_type,
                } for message in pending_messages
            ],
            'sent_messages': [
                {
                    'id': record.id,
                    'sent_at': record.sent_at,
                    'status': record.recurrence_type,  
                    'message_text': record.recurring_message.text,
                } for record in sent_messages
            ],
        }

     
        logger.info(f"Found {len(pending_messages)} pending messages and {len(sent_messages)} sent messages.")

 
        return JsonResponse(response_data)

    except Exception as e:
     
        logger.error(f"Error in monitor_recurring_messages: {e}")
        return JsonResponse({'error': 'An error occurred while fetching recurring messages.'}, status=500)
    

# Handle deletion of recurring messages

@csrf_exempt
def delete_recurring_message(request, recurring_message_id):
    """
    View to delete a recurring message based on its ID.
    """
    try:
   
        recurring_message = get_object_or_404(RecurringMessage, id=recurring_message_id)

    
        recurring_message.delete()

        activity = ActivityChannel.objects.create(
               user=request.user,
               action_type="PREVENT_RECURRING_MESSAGE",
               content=f'{request.user} prevent the message from recurrance -- {recurring_message.text}'

        )

     
        RecurrenceHistory.objects.filter(recurring_message=recurring_message).delete()

        return JsonResponse({'success': 'Recurring message deleted successfully.'}, status=200)

    except Exception as e:
        logger.error(f"Error deleting recurring message ID {recurring_message_id}: {e}")
        return JsonResponse({'error': 'An error occurred while deleting the recurring message.'}, status=500)



# RETRIVE ABUSED MESSAGES & WARN THE USER


# View 1: Fetch flagged messages

def fetch_flagged_messages(request, org_id, channel_id):
    """
    Fetch all flagged messages for a specific organization and channel.
    """
  
    organization = get_object_or_404(Organization, id=org_id)
    channel = get_object_or_404(Channel, id=channel_id, organization=organization)

    if request.user != organization.created_by:
        return JsonResponse({'error': 'You must be the admin of the organization to set policies.'}, status=403)
    
    user_profile = Profile.objects.filter(user=request.user,organization=organization).first()
   
    if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
          return JsonResponse({'error': 'You are not part of this organization or you do not have access to this channel.'}, status=403)

    abused_messages = AbusedMessage.objects.filter(organization=organization, channel=channel).select_related('flagged_by')

  
    messages_data = [
        {
            "id": message.id,
            "message_content": message.message_content,
            "flagged_by": message.flagged_by.username if message.flagged_by else "Unknown",
            "flagged_at": message.flagged_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for message in abused_messages
    ]


    return JsonResponse({"messages": messages_data})


# View 2: Warn the user who flagged the message
def warn_user(request, message_id):
    """
    Send a warning email to the user who flagged the message.
    """

    abused_message = get_object_or_404(AbusedMessage, id=message_id)


    if abused_message.flagged_by and abused_message.flagged_by.email:
       
        send_mail(
            subject="Warning Regarding Flagged Message",
            message=(
                f"Dear {abused_message.flagged_by.username},\n\n"
                "We have noticed that you flagged a message in the channel "
                f"'{abused_message.channel.name}' of the organization '{abused_message.organization.name}'. "
                "Please ensure this action was done with genuine intent. Abuse of the flagging system can lead to penalties.\n\n"
                "Thank you,\nSupport Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[abused_message.flagged_by.email],
        )

        try:
           activity=ActivityChannel.objects.create(
           user=request.user,
           action_type="WARN",
           content=f'{request.user} warned {abused_message.flagged_by.username} about their abusive message: {abused_message.message_content}'
          )
           
           
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Error creating activity log: {str(e)}"})

     
        return JsonResponse({"success": True, "message": "Warning email sent successfully."})
    else:
       
        return JsonResponse({"success": False, "error": "The user who flagged this message has no email associated."})



# HANDLE CHANNEL EVENT CREATION


@csrf_exempt
def save_event_data(request, org_id, channel_id):
    if request.method == "POST":
        try:
   
            data = json.loads(request.body)
            event_name = data.get("event_name", "").strip()
            event_date = data.get("event_date", None)
            event_details = data.get("event_details", "").strip()
            event_link=data.get('event_link',"").strip()
            event_attachment = request.FILES.get('event_attachment', None)

      
            if event_attachment:
                fs = FileSystemStorage()
                filename = fs.save(event_attachment.name, event_attachment)
                file_url = fs.url(filename)



            if not event_name or not event_date:
                return JsonResponse({'error': 'Event name and date are required.'}, status=400)

   
            organization = get_object_or_404(Organization, id=org_id)
            channel = get_object_or_404(Channel, id=channel_id)

         
            user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
            if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
                return JsonResponse({'error': 'You are not part of this organization or do not have access to this channel.'}, status=403)

       
            event, created = ChannelEvents.objects.update_or_create(
                user=request.user,
                organization=organization,
                channel=channel,
                event_name=event_name,
                defaults={
                    'event_date': event_date,
                    'event_details': event_details,
                    'event_link':event_link,
                  
                },
            )

       
            ActivityChannel.objects.create(
                user=request.user,
                channel=channel,
                organization=organization,
                action_type="SAVE_EVENT",
                content=f'{request.user} created/updated an event: {event_name} on {event_date}',
            )

  
            events = ChannelEvents.objects.filter(organization=organization, channel=channel).values(
                'event_name', 'event_date', 'event_details', 'event_link','event_attachment','id',
            )

         
            response = {
                'message': 'Event saved successfully.',
                'event_id': event.id,
                'status': 'created' if created else 'updated',
                'events': list(events)  
            }
            return JsonResponse(response, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == "GET":
        
        organization = get_object_or_404(Organization, id=org_id)
        channel = get_object_or_404(Channel, id=channel_id)
        events = ChannelEvents.objects.filter(organization=organization, channel=channel).values(
            'event_name', 'event_date', 'event_details', 'event_link','event_attachment','id',
        )
        return JsonResponse({'events': list(events)}, status=200)
    else:
        return JsonResponse({'error': 'Invalid HTTP method. Use POST or GET.'}, status=405)


# DISPLAY EVENT DETAILS TO CHANNEL MEMBERS 

def fetch_event_details(request, org_id, channel_id):
  
    organization = get_object_or_404(Organization, id=org_id)
    channel = get_object_or_404(Channel, id=channel_id, organization=organization)

    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
        return JsonResponse({'error': 'You are not part of this organization or do not have access to this channel.'}, status=403)

    

    events = ChannelEvents.objects.filter(organization=organization, channel=channel)

  
    event_data = []
    for event in events:
        event_data.append({
            'event_name': event.event_name,
            'id':event.id,
            'event_date': event.event_date.strftime("%B %d, %Y, %I:%M %p"),
            'event_details': event.event_details,
            'event_attachment': event.event_attachment.url if event.event_attachment else None,
            'event_link': event.event_link if event.event_link else None,
            'created_by': event.user.username,
        })

    return JsonResponse({'events': event_data})




# Mark attending the event

@csrf_exempt
def mark_attending(request, org_id, channel_id, event_id):

    organization = get_object_or_404(Organization, id=org_id)
    channel = get_object_or_404(Channel, id=channel_id, organization=organization)
    event = get_object_or_404(ChannelEvents, id=event_id, channel=channel, organization=organization)

    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
        return JsonResponse({'error': 'You are not part of this organization or do not have access to this channel.'}, status=403)


   
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': 'User must be logged in to mark attendance.'}, status=401)


    recipient_email = event.user.email  
    subject = f"Attendance Confirmation for {event.event_name}"
    message = (
        f"Hello {event.user.username},\n\n"
        f"The user {user.username} from the organization '{organization.name}' and channel '{channel.name}' "
        f"has marked themselves as attending your event '{event.event_name}'.\n\n"
        "Best regards,\nYour Team"
    )


    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,  
        recipient_list=[recipient_email],
    )

    activity = ActivityChannel.objects.create(
        user=user,
        channel=channel,
        organization=organization,
        action_type="ATTENDING_EVENT",
        content=f'{request.user} will be attending the event {event.event_name} on {event.event_date}'
    )


    return JsonResponse({'message': 'Attendance confirmed and notification sent.'})


# CONFIGURE CHANNEL SETTINGS
from .models import ChannelSettingsOrganization

@csrf_exempt
def channel_settings_view(request, org_id, channel_id):
    organization = get_object_or_404(Organization, id=org_id)
    channel = get_object_or_404(Channel, id=channel_id, organization=organization)

    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
        return JsonResponse({'error': 'You are not part of this organization or do not have access to this channel.'}, status=403)
    
    if request.user != organization.created_by:
        return JsonResponse({'error': 'You must be the admin of the organization to set policies.'}, status=403)

    if request.method == 'GET':
        try:
            settings = ChannelSettingsOrganization.objects.get(organization_id=org_id, channel_id=channel_id)
            data = {
                'allow_media_uploads': settings.allow_media_uploads,
                'allow_codes': settings.allow_codes,
                'secure_from_unwanted_requests': settings.secure_from_unwanted_requests,
                'allow_polls': settings.allow_polls,
                'allow_sharing_access_to_another_workspace': settings.allow_sharing_access_to_another_workspace,
                'track_abusive_messages': settings.track_abusive_messages,
                'allow_integrations': settings.allow_integrations,
                'integration_choices': settings.integration_choices,
            }
            return JsonResponse(data)
        except ChannelSettingsOrganization.DoesNotExist:
            return JsonResponse({'error': 'Settings not found'}, status=404)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)  

            settings, created = ChannelSettingsOrganization.objects.update_or_create(
                organization=organization,
                channel=channel,
                defaults={  
                    'allow_media_uploads': data.get('allow_media_uploads', False),
                    'allow_codes': data.get('allow_codes', False),
                    'secure_from_unwanted_requests': data.get('secure_from_unwanted_requests', False),
                    'allow_polls': data.get('allow_polls', False),
                    'allow_sharing_access_to_another_workspace': data.get('allow_sharing_access_to_another_workspace', False),
                    'track_abusive_messages': data.get('track_abusive_messages', False),
                    'allow_integrations': data.get('allow_integrations', False),
                    'integration_choices': data.get('integration_choices', ''),
                }
            )
            return JsonResponse({'message': 'Settings saved successfully'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)




# DISPLAY CHANNEL CALENDAR

def channel_events_calendar(request, org_id, channel_id):

    organization = get_object_or_404(Organization, id=org_id)
    channel = get_object_or_404(Channel, id=channel_id, organization=organization)

    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile and not ChannelAccess.objects.filter(channel_id=channel_id, granted_to_organization=organization, user=request.user).exists():
        return JsonResponse({'error': 'You are not part of this organization or do not have access to this channel.'}, status=403)
    

    events = ChannelEvents.objects.filter(organization=organization, channel=channel)
    print("EVENTS FOUND:",events)

    event_data = []
    for event in events:
        event_data.append({
            'id': event.id,
            'title': event.event_name,
            'start': event.event_date.isoformat(),  
            'end': event.event_date.isoformat(),  
            'details': event.event_details,
            'attachment': event.event_attachment.url if event.event_attachment else None,
            'link': event.event_link,
        })

 
    return JsonResponse(event_data, safe=False)


# Channel end --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



# CHANNEL_LIST FEATURES 

# Delete channel  (ADMIN ONLY)

@csrf_exempt
def delete_channel(request, org_id, channel_id):
    if request.method == "POST":
        password = request.POST.get('password')

  
        user = authenticate(username=request.user.username, password=password)
        if user is None:
            return JsonResponse({"success": False, "error": "Invalid password."}, status=403)

       
        organization = get_object_or_404(Organization, id=org_id)
        channel = get_object_or_404(Channel, id=channel_id, organization=organization)

        
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile:
           return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

        if channel.created_by != request.user:
            return JsonResponse({"success": False, "error": "You are not authorized to delete this channel."}, status=403)

     
        channel.delete()
        activity = ActivityChannel.objects.create(
          user=user,
 
          organization=organization,
          action_type="DELETE_CHANNEL",
          content=f'{request.user} deleted the channel {channel.name} and its no longer available!'
        )

        return JsonResponse({"success": True, "message": "Channel deleted successfully!"})

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)



# DOWNLOAD ALL CHANNEL DATA (ADMIN ONLY)

@login_required
def export_channel_data(request, org_id, channel_id):
    organization = get_object_or_404(Organization, id=org_id)
    channel = get_object_or_404(Channel, id=channel_id, organization=organization)

    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
           return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

    if channel.created_by != request.user:
            return JsonResponse({"success": False, "error": "You are not authorized to download this channel data."}, status=403)

    
 
    messages = Message.objects.filter(channel=channel, organization=organization)
    links = Link.objects.filter(channel=channel, organization=organization)
    activities = ActivityChannel.objects.filter(channel=channel, organization=organization)
    banned_users = Ban.objects.filter(channel=channel, organization=organization)
    channel_accesses = ChannelAccess.objects.filter(channel=channel, owning_organization=organization)
    events = ChannelEvents.objects.filter(channel=channel, organization=organization)
    abused_messages = AbusedMessage.objects.filter(channel=channel, organization=organization)


    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

   
    y_position = 670
    p.drawString(100, y_position, f"Channel Export: {channel.name}")
    p.drawString(100, y_position - 15, f"Organization: {organization.name}")
    p.drawString(100, y_position - 30, f"Export Date: {localtime().strftime('%Y-%m-%d %H:%M:%S')}")

    y_position -= 45
    p.drawString(100, y_position, "Messages:")
    for message in messages:
        y_position -= 15
        p.drawString(100, y_position, f"- {message.timestamp}: {message.content} (By {message.user.username})")


    y_position -= 30
    p.drawString(100, y_position, "Links:")
    for link in links:
        y_position -= 15
        p.drawString(100, y_position, f"- {link.timestamp}: {link.text} ({link.link})")


    y_position -= 30
    p.drawString(100, y_position, "Activities:")
    for activity in activities:
        y_position -= 15
        p.drawString(100, y_position, f"- {activity.timestamp}: {activity.get_action_type_display()} (By {activity.user.username})")


    y_position -= 30
    p.drawString(100, y_position, "Banned Users:")
    for ban in banned_users:
        y_position -= 15
        p.drawString(100, y_position, f"- {ban.user.username} banned by {ban.banned_by.username} until {ban.end_time if ban.end_time else 'Permanent'}")


    y_position -= 30
    p.drawString(100, y_position, "Channel Access:")
    for access in channel_accesses:
        y_position -= 15
        p.drawString(100, y_position, f"- {access.granted_to_organization.name} (By {access.granted_by.username})")


    y_position -= 30
    p.drawString(100, y_position, "Channel Events:")
    for event in events:
        y_position -= 15
        p.drawString(100, y_position, f"- {event.event_name} on {event.event_date} ({event.event_details})")


    y_position -= 30
    p.drawString(100, y_position, "Abused Messages:")
    for abused_message in abused_messages:
        y_position -= 15
        p.drawString(100, y_position, f"- {abused_message.message_content} (Flagged by {abused_message.flagged_by.username if abused_message.flagged_by else 'Unknown'})")


    p.save()

    activity = ActivityChannel.objects.create(
          user=request.user,
          organization=organization,
          channel=channel,
          action_type="DOWNLOAD_CHANNEL_DATA",
          content=f'{request.user} Downloaded all the channel data'
        )

   
    buffer.seek(0)
    response = StreamingHttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=channel_{channel.id}_export.pdf"
    return response



# REMOVE ACCESS OF THE ORGANIZATION (ADMIN ONLY)
@csrf_exempt
@login_required
def manage_channel_access(request, channel_id):
    try:
  
        channel = get_object_or_404(Channel, id=channel_id)

      
        if channel.created_by != request.user:
            return JsonResponse({"success": False, "error": "You are not authorized to download this channel data."}, status=403)


        if request.method == "GET":
           
            accesses = ChannelAccess.objects.filter(channel=channel)

      
            organizations_with_access = [
                {
                    'id': access.granted_to_organization.id,
                    'name': access.granted_to_organization.name,
                    'granted_at': access.granted_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'granted_by': access.granted_by.username
                }
                for access in accesses
            ]

            return JsonResponse({
                'status': 'success',
                'organizations': organizations_with_access
            })

        elif request.method == "POST":
            
            data = json.loads(request.body)
            organization_id = data.get('organization_id')

            
            organization = get_object_or_404(Organization, id=organization_id)

            access = ChannelAccess.objects.filter(channel=channel, granted_to_organization=organization).first()

            if not access:
                return JsonResponse({
                    'status': 'error',
                    'message': 'The specified organization does not have access to this channel.'
                })

    
            access.remove_access()

            activity = ActivityChannel.objects.create(
              user=request.user,
              channel=channel,
              action_type="REMOVE_CHANNEL_ACCESS",
             content=f'{request.user} Removed this channel access from {organization.name}'
           )

            return JsonResponse({
                'status': 'success',
                'message': f'Access removed for {organization.name} from channel {channel.name}.'
            })

    except Exception as e:
        
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })
    

# MANAGE PERMISSIONS (ADMIN ONLY) 


# Retrive & handle permissions
# Set up logging
logger = logging.getLogger(__name__)

@csrf_exempt
@login_required
def manage_user_permissions(request, org_id, channel_id, user_id):
    try:
    
        organization = get_object_or_404(Organization, id=org_id)
        logger.debug(f"Organization fetched: {organization.id}, {organization.name}")

        
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile:
            logger.debug(f"User {request.user.id} does not belong to this organization.")
            return JsonResponse({'error': 'You do not belong to this organization.'}, status=403)

        channel = get_object_or_404(Channel, id=channel_id, organization=organization)
        logger.debug(f"Channel fetched: {channel.id}, {channel.name}")

    
        user = get_object_or_404(User, id=user_id)


        user_permissions = Permission.objects.filter(
            user=user, 
            organization=organization, 
            channel=channel
        )
        logger.debug(f"Fetched {user_permissions.count()} permission(s) for user {user_id} in channel {channel.id}")

        
        assigned_permissions = []
        for permission in user_permissions:
            assigned_permissions.extend(permission.permissions)  
        logger.debug(f"Assigned permissions: {assigned_permissions}")

        available_permissions = [
            'can_suspend_users', 'can_share_audio', 'can_send_files', 'can_see_channel_activities', 
            'can_bypass_inappropriate_messages', 'can_edit_channel', 'bypass_message_deletion', 
            'can_invite_others', 'can_kick_users', 'can_manage_announcements', 'can_connect_integrations', 
            'can_use_advanced_search', 'can_configure_retention_settings', 'can_manage_shared_content'
        ]
        logger.debug(f"Available permissions: {available_permissions}")

        permissions_data = {
            'user_id': user_id,
            'assignedPermissions': assigned_permissions, 
            'availablePermissions': available_permissions
        }

        if request.method == 'GET':
            logger.debug(f"GET request: Returning permissions data for user {user_id}")
            return JsonResponse({'status': 'success', 'data': permissions_data})

        elif request.method == 'POST':
         
            data = json.loads(request.body.decode('utf-8'))
            new_permissions = data.get('permissions', [])
            logger.debug(f"POST request: New permissions received: {new_permissions}")

            for permission in new_permissions:
                
                existing_permission = Permission.objects.filter(
                    user=user, 
                    organization=organization, 
                    channel=channel,
                    permissions__contains=[permission]  
                ).first()

                if existing_permission:
                    logger.debug(f"Permission {permission} already exists for user {user_id} in channel {channel.id}. Skipping.")
                else:
                    # Save new permission
                    Permission.objects.create(
                        user=user, 
                        organization=organization, 
                        channel=channel, 
                        permissions=[permission],
                        granted_by=request.user
                    )
                    logger.debug(f"Granted permission: {permission} to user {user_id} in channel {channel.id}")

            return JsonResponse({'status': 'success', 'message': 'Permissions updated successfully.'})

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)})



# MANAGE BANNED USERS (ADMIN ONLY)

@csrf_exempt
@login_required
def manage_banned_users(request, org_id, channel_id):
    try:
    
        organization = get_object_or_404(Organization, id=org_id)
 
        channel = get_object_or_404(Channel, id=channel_id, organization=organization)

        if channel.created_by != request.user:
            return JsonResponse({"success": False, "error": "You are not authorized to perform this action!."}, status=403)
        
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile:
            logger.debug(f"User {request.user.id} does not belong to this organization.")
            return JsonResponse({'error': 'You do not belong to this organization.'}, status=403)

        if request.method == 'GET':
            banned_users = Ban.objects.filter(organization=organization, channel=channel)
            banned_user_data = []

     
            for ban in banned_users:
                ban_data = {
                    'user_id': ban.user.id,
                    'username': ban.user.username,
                    'reason': ban.reason,
                    'start_time': ban.start_time,
                    'end_time': ban.end_time,
                    'duration': ban.duration,
                    'is_active': ban.is_active(),
                }
                banned_user_data.append(ban_data)

            return JsonResponse({'status': 'success', 'banned_users': banned_user_data})

      
        elif request.method == 'POST':
            data = json.loads(request.body.decode('utf-8'))
            user_id_to_unban = data.get('user_id')
            user=get_object_or_404(User,id=user_id_to_unban)
            if user_id_to_unban:
              
                ban_to_unban = Ban.objects.filter(
                    user__id=user_id_to_unban,
                    organization=organization,
                    channel=channel
                ).first()

                if ban_to_unban:
                    
                    ban_to_unban.unban()
                    activity = ActivityChannel.objects.create(
                         user=request.user,
                         channel=channel,
                         organization=organization,
                         action_type="REVOKE_RESTRICTION",
                         content=f"{request.user} Revoked channel restriction for {user.username}"
                          )

                    return JsonResponse({'status': 'success', 'message': f'User {ban_to_unban.user.username} has been unbanned.'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Ban entry not found.'})

            return JsonResponse({'status': 'error', 'message': 'No user ID provided for unban.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    




# SEND ALERT NOTIFICATIONS IN CHANNEL (ADMIN ONLY)
@csrf_exempt
@login_required
def send_alert_notification(request, org_id, channel_id):
    try:
        
        organization = get_object_or_404(Organization, id=org_id)
        channel = get_object_or_404(Channel, id=channel_id, organization=organization)

    
        if request.method == 'POST':
            
            data = json.loads(request.body.decode('utf-8'))
            message = data.get('message', None)

         
            if message:
                alert = AlertNotification.objects.create(
                    organization=organization,
                    channel=channel,
                    created_by=request.user,
                    message=message,
                )

           
                return JsonResponse({
                    'status': 'success',
                    'message': 'Alert notification sent successfully.',
                    'alert_id': alert.id,
                    'message': alert.message,
                    'sent_at': alert.sent_at,
                })
            else:
              
                return JsonResponse({
                    'status': 'error',
                    'message': 'No message provided.'
                })

       
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method.'
        })

    except Exception as e:
       
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })