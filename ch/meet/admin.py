from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Meeting, Docs, Birthday, Reminder

@admin.register(Meeting)
class MeetingAdmin(ModelAdmin):
    list_display = [field.name for field in Meeting._meta.fields]

@admin.register(Docs)
class DocsAdmin(ModelAdmin):
    list_display = [field.name for field in Docs._meta.fields]

@admin.register(Birthday)
class BirthdayAdmin(ModelAdmin):
    list_display = [field.name for field in Birthday._meta.fields]

@admin.register(Reminder)
class ReminderAdmin(ModelAdmin):
    list_display = [field.name for field in Reminder._meta.fields]
