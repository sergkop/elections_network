from django.contrib import admin

from navigation.models import Page

class PageAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)

admin.site.register(Page, PageAdmin)
