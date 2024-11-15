from django.contrib import admin
from .models import Meeting, Docs, Birthday


# Register your models here.
admin.site.register(Meeting)
admin.site.register(Docs)
admin.site.register(Birthday)
