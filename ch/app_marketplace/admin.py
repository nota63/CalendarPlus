from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (MiniApp)
from django.utils.html import format_html

# Register your models here.

@admin.register(MiniApp)
class MiniAppAdmin(ModelAdmin):
    list_display = [field.name for field in MiniApp._meta.fields]
