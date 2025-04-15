from django.shortcuts import render, redirect, get_object_or_404
from conversation.models import Conversation, Message
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from accounts.models import Profile, Organization

# Create your views here.
# fetch users within the workspace

@login_required
def fetch_chat_users(request, org_id):
    profiles = Profile.objects.filter(organization_id=org_id).exclude(user=request.user)
    
    data = []
    for profile in profiles:
        data.append({
            'user_id': profile.user.id,
            'full_name': profile.full_name,
            'profile_picture': profile.profile_picture.url if profile.profile_picture else None
        })

    return JsonResponse({'users': data})

# Get Or Create the conversation
# @csrf_exempt
# @login_required
# def handle_chat(request):
#     if request.method == "POST":
#         receiver_id = request.POST.get("receiver_id")
#         text = request.POST.get("text")
#         org_id = request.POST.get("org_id")

#         if not receiver_id or not text:
#             return JsonResponse({'error': 'Missing required fields'}, status=400)

#         receiver = User.objects.get(id=receiver_id)

#         # Sort users to avoid duplicate conversation creation
#         user1, user2 = sorted([request.user, receiver], key=lambda u: u.id)

#         # Get or create conversation
#         conversation, created = Conversation.objects.get_or_create(
#             user1=user1,
#             user2=user2,
#             organization_id=org_id
#         )

#         # Save the message
#         message = Message.objects.create(
#             organization_id=org_id,
#             conversation=conversation,
#             sender=request.user,
#             text=text,
#             timestamp=now()
#         )

#         return JsonResponse({
#             'status': 'Message sent',
#             'message_id': message.id,
#             'timestamp': message.timestamp.strftime("%Y-%m-%d %H:%M"),
#         })

#     elif request.method == "GET":
#         receiver_id = request.GET.get("receiver_id")
#         org_id = request.GET.get("org_id")

#         if not receiver_id:
#             return JsonResponse({'error': 'Receiver ID missing'}, status=400)

#         receiver = User.objects.get(id=receiver_id)
#         user1, user2 = sorted([request.user, receiver], key=lambda u: u.id)

#         try:
#             conversation = Conversation.objects.get(
#                 user1=user1,
#                 user2=user2,
#                 organization_id=org_id
#             )
#         except Conversation.DoesNotExist:
#             return JsonResponse({'messages': []})  # No conversation yet

#         messages = conversation.messages.order_by("timestamp")
#         messages_data = [
#             {
#                 "id": msg.id,
#                 "sender": msg.sender.id,
#                 "text": msg.text,
#                 "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M"),
#                 "is_read": msg.is_read
#             }
#             for msg in messages
#         ]

#         return JsonResponse({"messages": messages_data})


@csrf_exempt
@login_required
def handle_chat(request):
    if request.method == "POST":
        receiver_id = request.POST.get("receiver_id")
        text = request.POST.get("text", "").strip()
        org_id = request.POST.get("org_id")
        code_snippet = request.POST.get("code_snippet", "").strip()
        uploaded_file = request.FILES.get("file")

        if not receiver_id or not (text or code_snippet or uploaded_file):
            return JsonResponse({'error': 'Missing message content'}, status=400)

        receiver = User.objects.get(id=receiver_id)
        user1, user2 = sorted([request.user, receiver], key=lambda u: u.id)

        # Get or create conversation
        conversation, created = Conversation.objects.get_or_create(
            user1=user1,
            user2=user2,
            organization_id=org_id
        )

        # Save the message
        message = Message.objects.create(
            organization_id=org_id,
            conversation=conversation,
            sender=request.user,
            text=text if text else None,
            code_snippet=code_snippet if code_snippet else None,
            file=uploaded_file if uploaded_file else None
        )

        return JsonResponse({
            'status': 'Message sent',
            'message_id': message.id,
            'timestamp': message.timestamp.strftime("%Y-%m-%d %H:%M"),
            'sender': request.user.id,
            'text': message.text,
            'file_url': message.file.url if message.file else None,
            'code_snippet': message.code_snippet
        })

    elif request.method == "GET":
        receiver_id = request.GET.get("receiver_id")
        org_id = request.GET.get("org_id")

        if not receiver_id:
            return JsonResponse({'error': 'Receiver ID missing'}, status=400)

        receiver = User.objects.get(id=receiver_id)
        user1, user2 = sorted([request.user, receiver], key=lambda u: u.id)

        try:
            conversation = Conversation.objects.get(
                user1=user1,
                user2=user2,
                organization_id=org_id
            )
        except Conversation.DoesNotExist:
            return JsonResponse({'messages': []})

        messages = conversation.messages.order_by("timestamp")
        messages_data = [
            {
                "id": msg.id,
                "sender": msg.sender.id,
                "text": msg.text,
                "file_url": msg.file.url if msg.file else None,
                "code_snippet": msg.code_snippet,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M"),
                "is_read": msg.is_read
            }
            for msg in messages
        ]

        return JsonResponse({"messages": messages_data})
