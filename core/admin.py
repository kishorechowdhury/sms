from django.contrib import admin
from django.conf.locale.en import formats as en_format

from .models import Project, Profile, ProjectMember, UserActivity, Ticket

en_format.DATE_FORMAT = "M d, Y"
en_format.DATETIME_FORMAT = "M d, Y h:i:s A"



class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'designation', 'sex')
    list_per_page = 10
admin.site.register(Profile, ProfileAdmin)

class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ('project', 'user')
    list_per_page = 10
    list_filter = ['project']
admin.site.register(ProjectMember, ProjectMemberAdmin)

class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 0

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'status')
    list_per_page = 10
    inlines = [ProjectMemberInline]
admin.site.register(Project, ProjectAdmin)

class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_date', 'action')
    list_per_page = 10
    list_filter = ['user', 'action_date']
admin.site.register(UserActivity, UserActivityAdmin)

class TicketAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'status')
    list_per_page = 10
    list_filter = ['project']
admin.site.register(Ticket, TicketAdmin)