from django.contrib import admin

from users.models import FriendsModel, ParticipationModel

class ParticipationModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'type')
    ordering = ('user__username',)
    search_fields = ('user__username',)

class FriendsModelAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2')
    ordering = ('user1__username',)
    search_fields = ('user1__username', 'user2__username')

admin.site.register(ParticipationModel, ParticipationModelAdmin)
admin.site.register(FriendsModel, FriendsModelAdmin)
