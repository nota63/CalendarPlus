from django.contrib import admin
from .models import Channel, Message, Link
# Register your models here.
admin.site.register(Channel)
admin.site.register(Message)
admin.site.register(Link)