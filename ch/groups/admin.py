from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Group, GroupMember, GroupInvitation, GroupEvent, GroupEventBooking, AbsentEvent, GroupEventReminder, GroupActivity

@admin.register(Group)
class GroupAdmin(ModelAdmin):
    list_display = ('name', 'organization', 'team_leader', 'created_at')
    search_fields = ('name', 'organization__name')
    list_filter = ('organization',)

@admin.register(GroupMember)
class GroupMemberAdmin(ModelAdmin):
    list_display = ('group', 'user', 'role', 'joined_at')
    search_fields = ('group__name', 'user__username')
    list_filter = ('role', 'group__organization')

@admin.register(GroupInvitation)
class GroupInvitationAdmin(ModelAdmin):
    list_display = [field.name for field in GroupInvitation._meta.fields]

@admin.register(GroupEventBooking)
class GroupEventBookingAdmin(ModelAdmin):
    list_display = [field.name for field in GroupEventBooking._meta.fields]

@admin.register(GroupEvent)
class GroupEventAdmin(ModelAdmin):
    list_display = [field.name for field in GroupEvent._meta.fields]

@admin.register(AbsentEvent)
class AbsentEventAdmin(ModelAdmin):
    list_display = [field.name for field in AbsentEvent._meta.fields]

@admin.register(GroupEventReminder)
class GroupEventReminderAdmin(ModelAdmin):
    list_display = [field.name for field in GroupEventReminder._meta.fields]

@admin.register(GroupActivity)
class GroupActivityAdmin(ModelAdmin):
    list_display = [field.name for field in GroupActivity._meta.fields]
