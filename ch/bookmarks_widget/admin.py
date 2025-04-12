from django.contrib import admin
from .models import BookMarksWidget,RecentActivity
from unfold.admin import ModelAdmin



# Register your models here.
@admin.register(BookMarksWidget)
class BookmarksAdmin(ModelAdmin):
  list_display = [field.name for field in BookMarksWidget._meta.fields]


@admin.register(RecentActivity)
class RecentWidgetAdmin(ModelAdmin):
  list_display = [field.name for field in RecentActivity._meta.fields]



