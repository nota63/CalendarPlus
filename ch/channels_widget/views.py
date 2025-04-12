from django.shortcuts import render, redirect, get_object_or_404
from organization_channels.models import Channel, Message
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.models import Profile, Organization
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import json
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
# Create your views here.

# fetch channels 
@login_required
def fetch_channels_by_org(request, org_id):
    try:
        channels = Channel.objects.filter(organization_id=org_id).order_by('-updated_at')

        channel_data = [
            {
                "id": channel.id,
                "name": channel.name,
                "type": channel.get_type_display(),
                "visibility": channel.get_visibility_display(),
                "created_by": channel.created_by.username,
                "created_at": channel.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for channel in channels
        ]

        return JsonResponse({"status": "success", "channels": channel_data})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
# fetch channel message
@login_required
def fetch_channel_messages(request, org_id, channel_id):
    channel = get_object_or_404(Channel, id=channel_id, organization_id=org_id)

    messages = (
        Message.objects.filter(channel=channel, parent__isnull=True)
        .select_related('user', 'organization')
        .prefetch_related('replies')
        .order_by('-timestamp')
    )

    data = []
    for msg in messages:
        profile = Profile.objects.filter(user=msg.user, organization_id=org_id).first()

        msg_data = {
            'id': msg.id,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M'),
            'user': {
                'username': msg.user.username,
                'full_name': profile.full_name if profile else '',
                'profile_picture': profile.profile_picture.url if profile and profile.profile_picture else None
            },
            'replies': []
        }

        for reply in msg.replies.all():
            reply_profile = Profile.objects.filter(user=reply.user, organization_id=org_id).first()
            msg_data['replies'].append({
                'id': reply.id,
                'content': reply.content,
                'timestamp': reply.timestamp.strftime('%Y-%m-%d %H:%M'),
                'user': {
                    'username': reply.user.username,
                    'full_name': reply_profile.full_name if reply_profile else '',
                    'profile_picture': reply_profile.profile_picture.url if reply_profile and reply_profile.profile_picture else None
                },
            })

        data.append(msg_data)

    return JsonResponse({'messages': data})




# save channel message 
@require_POST
@login_required
def send_message_widget(request):
    try:
        org_id = request.POST.get('org_id')
        channel_id = request.POST.get('channel_id')
        content = request.POST.get('content', '').strip()

        channel = get_object_or_404(Channel, id=channel_id, organization_id=org_id)
        organization = get_object_or_404(Organization, id=org_id)

        audio_file = request.FILES.get('audio')
        video_file = request.FILES.get('video')

        if not content and not audio_file and not video_file:
            return JsonResponse({'status': 'error', 'message': 'Empty message not allowed'}, status=400)

        message = Message.objects.create(
            channel=channel,
            user=request.user,
            content=content,
            organization=organization,
            audio=audio_file,
            video=video_file
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Message sent',
            'message_id': message.id
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
