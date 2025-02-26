from django.contrib import admin
from .models import TaskOrganization
from unfold.admin import ModelAdmin

# Register your models here.


@admin.register(TaskOrganization)
class TasksOrganizationAdmin(ModelAdmin):
    list_display = [field.name for field in TaskOrganization._meta.fields]

