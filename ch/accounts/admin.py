from django.contrib import admin
from .models import Availability, HolidayOrganization, HolidaySettings, HolidayType, MeetingOrganization, MeetingReminder

# Register your models here.
admin.site.register(Availability)
admin.site.register(HolidayOrganization)
admin.site.register(HolidaySettings)
admin.site.register(HolidayType)
admin.site.register(MeetingOrganization)
admin.site.register(MeetingReminder)

