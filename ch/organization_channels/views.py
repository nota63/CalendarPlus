from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import Organization, Profile
from .models import Channel
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import Http404
from formtools.wizard.views import SessionWizardView
from .forms import ChannelTypeForm, ChannelNameForm, ChannelVisibilityForm
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.db.models import Count
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
