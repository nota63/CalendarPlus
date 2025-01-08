from django.contrib import admin
from .models import Task, AddDay, TaskComment, TaskNote , TaskTag, TaskTimer


# Register your models here.
admin.site.register(Task)
admin.site.register(AddDay)
admin.site.register(TaskTag)
admin.site.register(TaskComment)
admin.site.register(TaskNote)
admin.site.register(TaskTimer)
