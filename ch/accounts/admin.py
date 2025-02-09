from django.contrib import admin
from .models import (Availability, HolidayOrganization, HolidaySettings, HolidayType, MeetingOrganization, MeetingReminder, Agenda, MeetingNotes, EventOrganization, BookingOrganization,
                     
                     Organization,Profile,Suspend
                     )

# Register your models here.
admin.site.register(Availability)
admin.site.register(HolidayOrganization)
admin.site.register(HolidaySettings)
admin.site.register(HolidayType)
admin.site.register(MeetingOrganization)
admin.site.register(MeetingReminder)
admin.site.register(Agenda)
admin.site.register(MeetingNotes)
admin.site.register(EventOrganization)
admin.site.register(BookingOrganization)
admin.site.register(Organization)
admin.site.register(Profile)
admin.site.register(Suspend)