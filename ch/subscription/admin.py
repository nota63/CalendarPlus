from django.contrib import admin
from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Payment, PremiumPlan, HelpRequest,ImpersonationActivityLog

@admin.register(Payment)
class PaymentsAdmin(ModelAdmin):
    list_display = [field.name for field in Payment._meta.fields]



@admin.register(PremiumPlan)
class PremiumPlansAdmin(ModelAdmin):
    list_display = [field.name for field in PremiumPlan._meta.fields]



@admin.register(HelpRequest)
class HelpRequestsAdmin(ModelAdmin):
    list_display = [field.name for field in HelpRequest._meta.fields]




@admin.register(ImpersonationActivityLog)
class HelpRequestsSummaryAdmin(ModelAdmin):
    list_display = [field.name for field in ImpersonationActivityLog._meta.fields]

