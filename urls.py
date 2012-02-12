from settings import ADMIN_PREFIX, DEBUG, STATIC_ROOT
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('grakon.urls')),
    url(r'^', include('navigation.urls')),
    url(r'^', include('users.urls')),
    url(r'^', include('reports.urls')),
    url(r'^', include('registration.urls')),
    #url(r'^', include('organizations.urls')),
    url(r'^links/', include('links.urls')),
    url(r'^location/', include('locations.urls')),
    url(r'^loginza/', include('loginza.urls')),
    (r'^tinymce/', include('tinymce.urls')),

    url(r'^%s/' % ADMIN_PREFIX, include(admin.site.urls)),
)

if DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': STATIC_ROOT}),
    )
