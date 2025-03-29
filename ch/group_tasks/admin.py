from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (Task, AddDay, TaskComment, TaskNote, TaskTag, TaskTimer, ActivityLog, TaskTimeTracking,
                     
                      Problem,AttachmentsTasksApp,RecentVisit,MeetingTaskQuery,CommunicateTask,SubTask,TaskReminder,CalPoints,
                      PendingRewardNotification,AutomationTask,TaskCompletionActivities,TaskBackup,ActivityBackup,
                      TaskProgressLog,Issue)


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



@admin.register(AttachmentsTasksApp)
class TaskAttachmentsAdmin(ModelAdmin):
    list_display = [field.name for field in AttachmentsTasksApp._meta.fields]



@admin.register(RecentVisit)
class RecentVisitsAdmin(ModelAdmin):
    list_display = [field.name for field in RecentVisit._meta.fields]



@admin.register(MeetingTaskQuery)
class MeetingTasksAdmin(ModelAdmin):
    list_display = [field.name for field in MeetingTaskQuery._meta.fields]


@admin.register(CommunicateTask)
class CommunicateTaskAdmin(ModelAdmin):
    list_display = [field.name for field in CommunicateTask._meta.fields]


@admin.register(SubTask)
class SubTaskAdmin(ModelAdmin):
    list_display = [field.name for field in SubTask._meta.fields]


@admin.register(TaskReminder)
class TaskRemindersAdmin(ModelAdmin):
    list_display = [field.name for field in TaskReminder._meta.fields]



@admin.register(CalPoints)
class CalpointsAdmin(ModelAdmin):
    list_display = [field.name for field in CalPoints._meta.fields]


@admin.register(PendingRewardNotification)
class PendingRewardNotificationAdmin(ModelAdmin):
    list_display = [field.name for field in PendingRewardNotification._meta.fields]


@admin.register(AutomationTask)
class AutomationAdmin(ModelAdmin):
    list_display = [field.name for field in AutomationTask._meta.fields]



@admin.register(TaskCompletionActivities)
class AutomationTaskCompletionLogsAdmin(ModelAdmin):
    list_display = [field.name for field in TaskCompletionActivities._meta.fields]




@admin.register(TaskBackup)
class TaskBackupsAdmin(ModelAdmin):
    list_display = [field.name for field in TaskBackup._meta.fields]



@admin.register(ActivityBackup)
class ActivityBackupsAdmin(ModelAdmin):
    list_display = [field.name for field in ActivityBackup._meta.fields]



@admin.register(TaskProgressLog)
class TasksProgressAdmin(ModelAdmin):
    list_display = [field.name for field in TaskProgressLog._meta.fields]




@admin.register(Issue)
class TasksIssuesAdmin(ModelAdmin):
    list_display = [field.name for field in Issue._meta.fields]


