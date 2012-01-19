from django.contrib import admin

from users.models import ContactModel, ParticipationModel, Profile, ReportUserModel

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    ordering = ('user__username',)
    search_fields = ('user__username',)

class ParticipationModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'type')
    ordering = ('user__username',)
    search_fields = ('user__username',)

class ContactModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact')
    ordering = ('user__username',)
    search_fields = ('user__username', 'contact__username')

class ReportUserModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'reporter')
    ordering = ('user__username',)
    search_fields = ('user__username', 'reporter__username')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(ParticipationModel, ParticipationModelAdmin)
admin.site.register(ContactModel, ContactModelAdmin)
admin.site.register(ReportUserModel, ReportUserModelAdmin)
