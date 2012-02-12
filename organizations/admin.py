from django.contrib import admin

from organizations.models import Organization, OrganizationCoverage

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'verified')
    ordering = ('title',)
    search_fields = ('title', 'name', 'address')

class OrganizationCoverageAdmin(admin.ModelAdmin):
    list_display = ('organization', 'location')
    ordering = ('organization', 'location')
    search_fields = ('organization__title', 'location__name')

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationCoverage, OrganizationCoverageAdmin)
