from django.contrib import admin
from .models import Task, AddDay, TaskComment, TaskNote , TaskTag, TaskTimer, ActivityLog, TaskTimeTracking,Problem


# Register your models here.
admin.site.register(Task)
admin.site.register(AddDay)
admin.site.register(TaskTag)
admin.site.register(TaskComment)
admin.site.register(TaskNote)
admin.site.register(TaskTimer)
admin.site.register(ActivityLog)
admin.site.register(TaskTimeTracking)
admin.site.register(Problem)

