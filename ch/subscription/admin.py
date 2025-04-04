from django.contrib import admin
from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Payment, PremiumPlan

@admin.register(Payment)
class PaymentsAdmin(ModelAdmin):
    list_display = [field.name for field in Payment._meta.fields]



@admin.register(PremiumPlan)
class PremiumPlansAdmin(ModelAdmin):
    list_display = [field.name for field in PremiumPlan._meta.fields]

