from django.contrib import admin
from .models import (Channel, Message, Link, Mention, ActivityChannel, Ban, ChannelAccess,RetentionPolicy,AbusedMessage,RecurringMessage,RecurrenceHistory,
                     
                     ChannelEvents, ChannelSettings)



@admin.register(ChannelSettings)
class ChannelSettingsAdmin(admin.ModelAdmin):
    list_display = ('channel', 'organization', 'created_by', 'created_at', 'updated_at')




# Register your models here.
admin.site.register(Channel)
admin.site.register(Message)
admin.site.register(Link)
admin.site.register(Mention)
admin.site.register(ActivityChannel)
admin.site.register(Ban)
admin.site.register(ChannelAccess)
admin.site.register(RetentionPolicy)
admin.site.register(AbusedMessage)
admin.site.register(RecurringMessage)
admin.site.register(RecurrenceHistory)
admin.site.register(ChannelEvents)

