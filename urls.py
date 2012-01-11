from settings import STATIC_ROOT
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': STATIC_ROOT}),
    url(r'^admin/', include(admin.site.urls)),

    # url(r'^$', 'elections_network.views.home', name='home'),
    url(r'^links/', include('links.urls')),
    url(r'^location/', include('geography.urls')),
    url(r'^', include('navigation.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^loginza/', include('loginza.urls')),
)
