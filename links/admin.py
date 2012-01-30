from django.contrib import admin

from links.models import Link

class LinkAdmin(admin.ModelAdmin):
    list_display = ('url', 'name', 'location', 'user')
    ordering = ('url',)
    search_fields = ('url', 'location', 'name', 'user')

admin.site.register(Link, LinkAdmin)
