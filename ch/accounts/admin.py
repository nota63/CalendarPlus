from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (
    Availability, HolidayOrganization, HolidaySettings, HolidayType, 
    MeetingOrganization, MeetingReminder, Agenda, MeetingNotes, 
    EventOrganization, BookingOrganization, Organization, Profile, Suspend
)

@admin.register(Availability)
class AvailabilityAdmin(ModelAdmin):
    list_display = [field.name for field in Availability._meta.fields]

@admin.register(HolidayOrganization)
class HolidayOrganizationAdmin(ModelAdmin):
    list_display = [field.name for field in HolidayOrganization._meta.fields]

@admin.register(HolidaySettings)
class HolidaySettingsAdmin(ModelAdmin):
    list_display = [field.name for field in HolidaySettings._meta.fields]

@admin.register(HolidayType)
class HolidayTypeAdmin(ModelAdmin):
    list_display = [field.name for field in HolidayType._meta.fields]

@admin.register(MeetingOrganization)
class MeetingOrganizationAdmin(ModelAdmin):
    list_display = [field.name for field in MeetingOrganization._meta.fields]

@admin.register(MeetingReminder)
class MeetingReminderAdmin(ModelAdmin):
    list_display = [field.name for field in MeetingReminder._meta.fields]

@admin.register(Agenda)
class AgendaAdmin(ModelAdmin):
    list_display = [field.name for field in Agenda._meta.fields]

@admin.register(MeetingNotes)
class MeetingNotesAdmin(ModelAdmin):
    list_display = [field.name for field in MeetingNotes._meta.fields]

@admin.register(EventOrganization)
class EventOrganizationAdmin(ModelAdmin):
    list_display = [field.name for field in EventOrganization._meta.fields]

@admin.register(BookingOrganization)
class BookingOrganizationAdmin(ModelAdmin):
    list_display = [field.name for field in BookingOrganization._meta.fields]


@admin.register(Organization)
class OrganizationAdmin(ModelAdmin):
    list_display = [field.name for field in Organization._meta.fields]
    


@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = [field.name for field in Profile._meta.fields]

@admin.register(Suspend)
class SuspendAdmin(ModelAdmin):
    list_display = [field.name for field in Suspend._meta.fields]

