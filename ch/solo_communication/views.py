from django.shortcuts import render
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message
# Create your views here.


@login_required
def home(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, "one-on-one/chats/chats.html", {"users": users})


@login_required
def chat_view(request, username):
    other_user = User.objects.get(username=username)
    messages = Message.objects.filter(
        sender=request.user, receiver=other_user
    ) | Message.objects.filter(
        sender=other_user, receiver=request.user
    )
    messages = messages.order_by("timestamp")  # Ensure correct order
    return render(request, "one-on-one/chats/start.html", {"other_user": other_user, "messages": messages})
