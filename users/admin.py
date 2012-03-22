from django.contrib import admin

from users.models import *

class RoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'type', 'verified')
    ordering = ('user__username',)
    search_fields = ('user__username', 'user__user__email')
    raw_id_fields = ('location', 'user')

class ContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact')
    ordering = ('user__username',)
    search_fields = ('user__username', 'contact__username')
    raw_id_fields = ('contact', 'user')

class CommissionMemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'role', 'party', 'location', 'user')
    ordering = ('last_name',)
    search_fields = ('last_name', 'party', 'location__name')
    raw_id_fields = ('location', 'user')

class WebObserverAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'capture_video', 'location', 'user', 'url')
    ordering = ('start_time', 'location')
    search_fields = ('start_time', 'location__name', 'user__username')
    raw_id_fields = ('location', 'user')

class MessageAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'title', 'show_email')
    ordering = ('time',)
    search_fields = ('from_user__user__username', 'from_user__user__email',
            'to_user__user__email', 'to_user__user__email')
    raw_id_fields = ('from_user', 'to_user')

class UnsubscribedUserAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__user__email', 'user__username')
    raw_id_fields = ('user',)

admin.site.register(Role, RoleAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(CommissionMember, CommissionMemberAdmin)
admin.site.register(WebObserver, WebObserverAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(UnsubscribedUser, UnsubscribedUserAdmin)
