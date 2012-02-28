from django.contrib import admin

from users.models import CommissionMember, Contact, Role

class RoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'type', 'verified')
    ordering = ('user__username',)
    search_fields = ('user__username',)

class ContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact')
    ordering = ('user__username',)
    search_fields = ('user__username', 'contact__username')

class CommissionMemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'role', 'party', 'location', 'user')
    ordering = ('last_name',)
    search_fields = ('last_name', 'party', 'location__name')

admin.site.register(Role, RoleAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(CommissionMember, CommissionMemberAdmin)
