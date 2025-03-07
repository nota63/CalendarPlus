from django.contrib import admin
from .models import AutoSchedule
from unfold.admin import ModelAdmin

# Register your models here.

@admin.register(AutoSchedule)
class AutoScheduleAdmin(ModelAdmin):
    list_display = [field.name for field in AutoSchedule._meta.fields]

