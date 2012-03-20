from django.contrib import admin

from locations.models import Boundary, Location

class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'region', 'tik')
    ordering = ('id',)
    search_fields = ('id', 'tvd', 'region_name', 'vrnkomis', 'vrnorg', 'root', 'name')
    raw_id_fields = ('region', 'tik')

class BoundaryAdmin(admin.ModelAdmin):
    list_display = ('x_min', 'x_max', 'y_min', 'y_max')

admin.site.register(Location, LocationAdmin)
admin.site.register(Boundary, BoundaryAdmin)
