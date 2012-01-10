from django.contrib import admin

from users.models import ParticipationModel

class ParticipationModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'type')
    ordering = ('user__username',)
    search_fields = ('user__username',)

admin.site.register(ParticipationModel, ParticipationModelAdmin)
