from django.shortcuts import render, redirect, get_object_or_404
from organization_channels.models import Channel, Message
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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