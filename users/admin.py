from django.contrib import admin

from users.models import Contact, Participation, Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    ordering = ('user__username',)
    search_fields = ('user__username',)

class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'type')
    ordering = ('user__username',)
    search_fields = ('user__username',)

class ContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact')
    ordering = ('user__username',)
    search_fields = ('user__username', 'contact__username')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(Contact, ContactAdmin)

