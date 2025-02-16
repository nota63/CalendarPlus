from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Task, AddDay, TaskComment, TaskNote, TaskTag, TaskTimer, ActivityLog, TaskTimeTracking, Problem

@admin.register(Task)
class TaskAdmin(ModelAdmin):
    list_display = [field.name for field in Task._meta.fields]

@admin.register(AddDay)
class AddDayAdmin(ModelAdmin):
    list_display = [field.name for field in AddDay._meta.fields]

@admin.register(TaskTag)
class TaskTagAdmin(ModelAdmin):
    list_display = [field.name for field in TaskTag._meta.fields]

@admin.register(TaskComment)
class TaskCommentAdmin(ModelAdmin):
    list_display = [field.name for field in TaskComment._meta.fields]

@admin.register(TaskNote)
class TaskNoteAdmin(ModelAdmin):
    list_display = [field.name for field in TaskNote._meta.fields]

@admin.register(TaskTimer)
class TaskTimerAdmin(ModelAdmin):
    list_display = [field.name for field in TaskTimer._meta.fields]

@admin.register(ActivityLog)
class ActivityLogAdmin(ModelAdmin):
    list_display = [field.name for field in ActivityLog._meta.fields]

@admin.register(TaskTimeTracking)
class TaskTimeTrackingAdmin(ModelAdmin):
    list_display = [field.name for field in TaskTimeTracking._meta.fields]

@admin.register(Problem)
class ProblemAdmin(ModelAdmin):
    list_display = [field.name for field in Problem._meta.fields]

