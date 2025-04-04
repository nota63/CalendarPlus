from django.contrib import admin
from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Payment

@admin.register(Payment)
class PaymentsAdmin(ModelAdmin):
    list_display = [field.name for field in Payment._meta.fields]

