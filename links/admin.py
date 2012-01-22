from django.contrib import admin

from links.models import Link, ReportLink

class LinkAdmin(admin.ModelAdmin):
    list_display = ('url', 'name', 'location', 'user')
    ordering = ('url',)
    search_fields = ('url', 'location', 'name', 'user')

class ReportLinkAdmin(admin.ModelAdmin):
    list_display = ('link', 'user')
    ordering = ('link',)
    search_fields = ('link__url', 'user')

admin.site.register(Link, LinkAdmin)
admin.site.register(ReportLink, ReportLinkAdmin)
