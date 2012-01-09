from django.contrib import admin

from geography.models import LocationModel

class LocationModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_1')
    ordering = ('name',)
    search_fields = ('name',)

admin.site.register(LocationModel, LocationModelAdmin)
