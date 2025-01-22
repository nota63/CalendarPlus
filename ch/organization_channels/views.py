from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import Organization, Profile
from .models import (
    Channel, Message, Link , ActivityChannel, ChannelAccess)
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
from django.http import JsonResponse
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
        }
        return render(request, self.template_name, context)






# Redirect to channel room

def channel_chat(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id)
    messages = Message.objects.filter(channel=channel).order_by('timestamp')
    links = Link.objects.filter(channel=channel).order_by('timestamp')


    ban_entry = Ban.objects.filter(
        user=request.user,
        channel=channel,
        organization=channel.organization,
    ).first()

    if ban_entry:
        
        if ban_entry.end_time is None or ban_entry.end_time > now():
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


    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)


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

    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

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
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

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
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

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

        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile:
           return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

        
     
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

        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile:
           return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

      
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
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

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

    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)


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

        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile:
           return JsonResponse({'error': 'You are not part of this organization.'}, status=403)


   
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

        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile:
           return JsonResponse({'error': 'You are not part of this organization.'}, status=403)


   
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
            user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
            if not user_profile:
               return JsonResponse({'error': 'You are not part of this organization.'}, status=403)


     
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

          
            user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
            if not user_profile:
                return JsonResponse({'error': 'You are not part of this organization.'}, status=403)


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
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
                return JsonResponse({'error': 'You are not part of this organization.'}, status=403)
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

    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)


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
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile:
           return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

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

        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile:
           return JsonResponse({'error': 'You are not part of this organization.'}, status=403)


  
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
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

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
    Fetch all organizations where the request.user is an admin.
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
        - Description: {channel.description}
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






