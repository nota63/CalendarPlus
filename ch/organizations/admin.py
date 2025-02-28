from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import OrganizationHide, RecurringMeeting,Help

@admin.register(OrganizationHide)
class OrganizationHideAdmin(ModelAdmin):
    list_display = [field.name for field in OrganizationHide._meta.fields]

@admin.register(RecurringMeeting)
class RecurringMeetingAdmin(ModelAdmin):
    list_display = [field.name for field in RecurringMeeting._meta.fields]



admin.site.register(Help)
