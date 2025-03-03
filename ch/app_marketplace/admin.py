from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (MiniApp,MiniAppImage)
from django.utils.html import format_html

# Register your models here.

@admin.register(MiniApp)
class MiniAppAdmin(ModelAdmin):
    list_display = [field.name for field in MiniApp._meta.fields]



@admin.register(MiniAppImage)
class MiniAppImageAdmin(ModelAdmin):
    list_display = [field.name for field in MiniAppImage._meta.fields]
