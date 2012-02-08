from django.contrib import admin

from grakon.models import Profile
from users.models import Contact

class ContactInline(admin.TabularInline):
    model = Contact
    fk_name = 'user'

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'show_name')
    ordering = ('user__username',)
    search_fields = ('user__username',)
    inlines = [ContactInline]

admin.site.register(Profile, ProfileAdmin)