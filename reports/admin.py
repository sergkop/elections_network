from django.contrib import admin

from reports.models import Report

class ReportAdmin(admin.ModelAdmin):
    list_display = ('item', 'reporter', 'reason', 'time')
    ordering = ('time',)
    search_fields = ('reporter', 'reason')

admin.site.register(Report, ReportAdmin)
