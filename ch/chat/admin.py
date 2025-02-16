from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Room

@admin.register(Room)
class RoomAdmin(ModelAdmin):
    list_display = [field.name for field in Room._meta.fields]
