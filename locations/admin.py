from django.contrib import admin

from locations.models import Location

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'tik')
    ordering = ('name',)
    search_fields = ('name',) #  'region_name'
    raw_id_fields = ('region', 'tik')

admin.site.register(Location, LocationAdmin)
