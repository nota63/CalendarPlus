from django.contrib import admin
from .models import (Channel, Message, Link, Mention, ActivityChannel, Ban, ChannelAccess,RetentionPolicy,AbusedMessage,RecurringMessage,RecurrenceHistory)


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

