from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ActivityLog

@admin.register(ActivityLog)
class ActivityLogAdmin(ModelAdmin):
    list_display = [field.name for field in ActivityLog._meta.fields]
