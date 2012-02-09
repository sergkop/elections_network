from django.contrib import admin

from locations.models import Location

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'tik')
    ordering = ('name',)
    search_fields = ('name',) #  'region_name'

admin.site.register(Location, LocationAdmin)
