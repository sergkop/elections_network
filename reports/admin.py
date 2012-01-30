from django.contrib import admin

from reports.models import ReportLink, ReportUser

class ReportLinkAdmin(admin.ModelAdmin):
    list_display = ('link', 'user')
    ordering = ('link',)
    search_fields = ('link__url', 'user')

class ReportUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'reporter')
    ordering = ('user__username',)
    search_fields = ('user__username', 'reporter__username')

admin.site.register(ReportLink, ReportLinkAdmin)
admin.site.register(ReportUser, ReportUserAdmin)
