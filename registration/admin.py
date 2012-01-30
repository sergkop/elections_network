from django.contrib import admin

from registration.models import RegistrationProfile

class RegistrationAdmin(admin.ModelAdmin):
    actions = ['activate_users', 'resend_activation_email']
    list_display = ('user', 'activation_key_expired')
    raw_id_fields = ['user']
    search_fields = ('user__username', 'user__first_name')

    def activate_users(self, request, queryset):
        """ Activates the selected users, if they are not already activated """
        for profile in queryset:
            RegistrationProfile.objects.activate_user(profile.activation_key)
    activate_users.short_description = "Activate users"

    def resend_activation_email(self, request, queryset):
        for profile in queryset:
            if not profile.activation_key_expired():
                profile.send_activation_email(site)
    resend_activation_email.short_description = "Re-send activation emails"

admin.site.register(RegistrationProfile, RegistrationAdmin)
