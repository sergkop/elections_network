from django.contrib import admin

from protocols.models import AttachedFile, Protocol

class ProtocolAdmin(admin.ModelAdmin):
    list_display = ('source', 'p19', 'p20', 'p21', 'p22', 'p23', 'verified')
    raw_id_fields = ('location',)

class AttachedFileAdmin(admin.ModelAdmin):
    list_display = ('item', 'internal', 'url')

admin.site.register(Protocol, ProtocolAdmin)
admin.site.register(AttachedFile, AttachedFileAdmin)
