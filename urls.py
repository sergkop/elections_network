from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('grakon.urls')),
    url(r'^', include('navigation.urls')),
    url(r'^', include('users.urls')),
    url(r'^', include('reports.urls')),
    url(r'^', include('registration.urls')),
    url(r'^organization/', include('organizations.urls')),
    url(r'^links/', include('links.urls')),
    url(r'^location/', include('locations.urls')),
    url(r'^loginza/', include('loginza.urls')),
    (r'^tinymce/', include('tinymce.urls')),

    url(r'^%s/' % settings.ADMIN_PREFIX, include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True)
