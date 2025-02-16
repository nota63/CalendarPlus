from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import GoogleAuth

@admin.register(GoogleAuth)
class GoogleAuthAdmin(ModelAdmin):
    list_display = [field.name for field in GoogleAuth._meta.fields]

