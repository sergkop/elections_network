from django.contrib import admin

from violations.models import Violation

class ViolationAdmin(admin.ModelAdmin):
    list_display = ('source', 'violation_id', 'type', 'url', 'time')
    ordering = ('time',)
    search_fields = ('voilation_id', 'type')
    raw_id_fields = ('location',)

admin.site.register(Violation, ViolationAdmin)
