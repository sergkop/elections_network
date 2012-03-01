from django.contrib import admin

from users.models import CommissionMember, Contact, Role, WebObserver

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
    list_display = ('start_time', 'end_time', 'capture_video', 'location', 'user')
    ordering = ('start_time', 'location')
    search_fields = ('start_time', 'location__name')
    raw_id_fields = ('location', 'user')

admin.site.register(Role, RoleAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(CommissionMember, CommissionMemberAdmin)
admin.site.register(WebObserver, WebObserverAdmin)
