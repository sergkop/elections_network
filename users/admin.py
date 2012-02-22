from django.contrib import admin

from users.models import Contact, Role

class RoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'type', 'verified')
    ordering = ('user__username',)
    search_fields = ('user__username',)

class ContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact')
    ordering = ('user__username',)
    search_fields = ('user__username', 'contact__username')

admin.site.register(Role, RoleAdmin)
admin.site.register(Contact, ContactAdmin)
