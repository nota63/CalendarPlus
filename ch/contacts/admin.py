from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ContactsOrganization, EmailOrganization, ScheduledEmail

@admin.register(ContactsOrganization)
class ContactsOrganizationAdmin(ModelAdmin):
    list_display = [field.name for field in ContactsOrganization._meta.fields]

@admin.register(EmailOrganization)
class EmailOrganizationAdmin(ModelAdmin):
    list_display = [field.name for field in EmailOrganization._meta.fields]

@admin.register(ScheduledEmail)
class ScheduledEmailAdmin(ModelAdmin):
    list_display = [field.name for field in ScheduledEmail._meta.fields]
