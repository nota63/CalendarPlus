from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Conversation, Message

@admin.register(Conversation)
class ConversationAdmin(ModelAdmin):
    list_display = [field.name for field in Conversation._meta.fields]

@admin.register(Message)
class MessageAdmin(ModelAdmin):
    list_display = [field.name for field in Message._meta.fields]
