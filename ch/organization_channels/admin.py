from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (
    Channel, Message, Link, Mention, ActivityChannel, Ban, ChannelAccess, 
    RetentionPolicy, AbusedMessage, RecurringMessage, RecurrenceHistory, 
    ChannelEvents, ChannelSettingsOrganization, Permission, AlertNotification
)

@admin.register(Channel)
class ChannelAdmin(ModelAdmin):
    list_display = [field.name for field in Channel._meta.fields]

@admin.register(Message)
class MessageAdmin(ModelAdmin):
    list_display = [field.name for field in Message._meta.fields]

@admin.register(Link)
class LinkAdmin(ModelAdmin):
    list_display = [field.name for field in Link._meta.fields]

@admin.register(Mention)
class MentionAdmin(ModelAdmin):
    list_display = [field.name for field in Mention._meta.fields]

@admin.register(ActivityChannel)
class ActivityChannelAdmin(ModelAdmin):
    list_display = [field.name for field in ActivityChannel._meta.fields]

@admin.register(Ban)
class BanAdmin(ModelAdmin):
    list_display = [field.name for field in Ban._meta.fields]

@admin.register(ChannelAccess)
class ChannelAccessAdmin(ModelAdmin):
    list_display = [field.name for field in ChannelAccess._meta.fields]

@admin.register(RetentionPolicy)
class RetentionPolicyAdmin(ModelAdmin):
    list_display = [field.name for field in RetentionPolicy._meta.fields]

@admin.register(AbusedMessage)
class AbusedMessageAdmin(ModelAdmin):
    list_display = [field.name for field in AbusedMessage._meta.fields]

@admin.register(RecurringMessage)
class RecurringMessageAdmin(ModelAdmin):
    list_display = [field.name for field in RecurringMessage._meta.fields]

@admin.register(RecurrenceHistory)
class RecurrenceHistoryAdmin(ModelAdmin):
    list_display = [field.name for field in RecurrenceHistory._meta.fields]

@admin.register(ChannelEvents)
class ChannelEventsAdmin(ModelAdmin):
    list_display = [field.name for field in ChannelEvents._meta.fields]

@admin.register(ChannelSettingsOrganization)
class ChannelSettingsOrganizationAdmin(ModelAdmin):
    list_display = [field.name for field in ChannelSettingsOrganization._meta.fields]

@admin.register(Permission)
class PermissionAdmin(ModelAdmin):
    list_display = [field.name for field in Permission._meta.fields]

@admin.register(AlertNotification)
class AlertNotificationAdmin(ModelAdmin):
    list_display = [field.name for field in AlertNotification._meta.fields]
