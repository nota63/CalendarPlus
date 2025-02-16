from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Profile, Organization

@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = [field.name for field in Profile._meta.fields]

@admin.register(Organization)
class OrganizationAdmin(ModelAdmin):
    list_display = [field.name for field in Organization._meta.fields]
