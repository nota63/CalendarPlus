from django.contrib import admin
from .models import ContactsOrganization, EmailOrganization, ScheduledEmail
# Register your models here.

admin.site.register(ContactsOrganization)
admin.site.register(EmailOrganization)
admin.site.register(ScheduledEmail)
