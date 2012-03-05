from django.contrib import admin

from protocols.models import Protocol

class ProtocolAdmin(admin.ModelAdmin):
    list_display = ('source', 'p19', 'p20', 'p21', 'p22', 'p23', 'verified')
    raw_id_fields = ('location',)

admin.site.register(Protocol, ProtocolAdmin)
