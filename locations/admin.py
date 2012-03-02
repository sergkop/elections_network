from django.contrib import admin

from locations.models import Location

class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'region', 'tik')
    ordering = ('id',)
    search_fields = ('id',) #  'region_name'
    raw_id_fields = ('region', 'tik')

admin.site.register(Location, LocationAdmin)
