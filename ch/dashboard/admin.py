from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import DashboardWidget
# Register your models here.



@admin.register(DashboardWidget)
class DashboardWidgetAdmin(ModelAdmin):
    list_display = [field.name for field in DashboardWidget._meta.fields]
