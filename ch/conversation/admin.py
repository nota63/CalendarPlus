from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Conversation, Message, MessageSuggestion, ScheduledMessage,Todo

@admin.register(Conversation)
class ConversationAdmin(ModelAdmin):
    list_display = [field.name for field in Conversation._meta.fields]

@admin.register(Message)
class MessageAdmin(ModelAdmin):
    list_display = [field.name for field in Message._meta.fields]


@admin.register(MessageSuggestion)
class MessageSuggestionAdmin(ModelAdmin):
    list_display = [field.name for field in MessageSuggestion._meta.fields]



@admin.register(ScheduledMessage)
class ScheduledMessagesAdmin(ModelAdmin):
    list_display = [field.name for field in ScheduledMessage._meta.fields]



@admin.register(Todo)
class TodoAdmin(ModelAdmin):
    list_display = [field.name for field in Todo._meta.fields]

