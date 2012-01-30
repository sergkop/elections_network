from django.contrib import admin

from locations.models import Location

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_1', 'parent_2')
    ordering = ('name',)
    search_fields = ('name',)

admin.site.register(Location, LocationAdmin)
