from django.contrib import admin
from .models import Group, GroupMember, GroupInvitation, GroupEvent, GroupEventBooking, AbsentEvent, GroupEventReminder, GroupActivity
# Register your models here.


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'team_leader', 'created_at')
    search_fields = ('name', 'organization__name')
    list_filter = ('organization',)


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'role', 'joined_at')
    search_fields = ('group__name', 'user__username')
    list_filter = ('role', 'group__organization')



admin.site.register(GroupInvitation)
admin.site.register(GroupEventBooking)
admin.site.register(GroupEvent)
admin.site.register(AbsentEvent)
admin.site.register(GroupEventReminder)
admin.site.register(GroupActivity)

