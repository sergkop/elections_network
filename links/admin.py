from django.contrib import admin

from links.models import LinkModel

class LinkModelAdmin(admin.ModelAdmin):
    list_display = ('url', 'name', 'location', 'user')
    ordering = ('url',)
    search_fields = ('url', 'location', 'name', 'user')

admin.site.register(LinkModel, LinkModelAdmin)
