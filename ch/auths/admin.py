from django.contrib import admin
from .models import Profile, Organization, Availability, Meets, Reminder, MeetInvitation, Contacts,FavoriteContact


# Register your models here.
admin.site.register(Profile)
admin.site.register(Organization)
admin.site.register(Availability)
admin.site.register(Meets)
admin.site.register(Reminder)
admin.site.register(MeetInvitation)
admin.site.register(Contacts)
admin.site.register(FavoriteContact)



