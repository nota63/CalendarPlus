from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (MiniApp,MiniAppImage,InstalledMiniApp,TaskManager)
from django.utils.html import format_html

# Register your models here.

@admin.register(MiniApp)
class MiniAppAdmin(ModelAdmin):
  list_display = ["name", "category", "developer", "version", "install_count", "is_premium"]



@admin.register(MiniAppImage)
class MiniAppImageAdmin(ModelAdmin):
    list_display = [field.name for field in MiniAppImage._meta.fields]



@admin.register(InstalledMiniApp)
class InstalledMiniAppAdmin(ModelAdmin):
    list_display = [field.name for field in InstalledMiniApp._meta.fields]



@admin.register(TaskManager)
class TaskManagerAdmin(ModelAdmin):
    list_display = [field.name for field in TaskManager._meta.fields]

