from django.contrib import admin

from organizations.models import Organization, OrganizationCoverage, OrganizationRepresentative

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'verified')
    ordering = ('title',)
    search_fields = ('title', 'name', 'address')

class OrganizationCoverageAdmin(admin.ModelAdmin):
    list_display = ('organization', 'location')
    ordering = ('organization', 'location')
    search_fields = ('organization__title', 'location__name')

class OrganizationRepresentativeAdmin(admin.ModelAdmin):
    list_display = ('organization', 'user')
    ordering = ('organization', 'user__username')
    search_fields = ('organization__title', 'user__username')

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationCoverage, OrganizationCoverageAdmin)
admin.site.register(OrganizationRepresentative, OrganizationRepresentativeAdmin)
