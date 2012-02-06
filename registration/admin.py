# -*- coding:utf-8 -*-
from django.contrib import admin

from registration.models import ActivationProfile

class ActivationProfileAdmin(admin.ModelAdmin):
    actions = ['activate_users', 'resend_activation_email']
    list_display = ('user', 'activation_key_expired')
    raw_id_fields = ['user']
    search_fields = ('user__username', 'user__first_name')

    def activate_users(self, request, queryset):
        for profile in queryset:
            ActivationProfile.objects.activate_user(profile.activation_key)
    activate_users.short_description = u'Активировать пользователей'

    def resend_activation_email(self, request, queryset):
        for profile in queryset:
            if not profile.activation_key_expired():
                profile.send_activation_email()
    resend_activation_email.short_description = u'Отправить активационные письма снова'

admin.site.register(ActivationProfile, ActivationProfileAdmin)
