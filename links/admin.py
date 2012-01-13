from django.contrib import admin

from links.models import LinkModel, ReportLinkModel

class LinkModelAdmin(admin.ModelAdmin):
    list_display = ('url', 'name', 'location', 'user')
    ordering = ('url',)
    search_fields = ('url', 'location', 'name', 'user')

class ReportLinkModelAdmin(admin.ModelAdmin):
    list_display = ('link', 'user')
    ordering = ('link',)
    search_fields = ('link__url', 'user')

admin.site.register(LinkModel, LinkModelAdmin)
admin.site.register(ReportLinkModel, ReportLinkModelAdmin)
