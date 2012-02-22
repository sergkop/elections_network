from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.simple import direct_to_template

from locations.sitemap import LocationSitemap
from organizations.sitemap import OrganizationSitemap

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('grakon.urls')),
    url(r'^', include('navigation.urls')),
    url(r'^', include('users.urls')),
    url(r'^', include('reports.urls')),
    url(r'^', include('registration.urls')),
    url(r'^', include('organizations.urls')),
    url(r'^links/', include('links.urls')),
    url(r'^location/', include('locations.urls')),
    url(r'^loginza/', include('loginza.urls')),
    url(r'^tinymce/', include('tinymce.urls')),

    (r'^robots\.txt$', direct_to_template, {'template': 'robots.txt', 'mimetype': 'text/plain'}),
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': {
        'locations': LocationSitemap,
        'organizations': OrganizationSitemap,
    }}),

    url(r'^%s/' % settings.ADMIN_PREFIX, include(admin.site.urls)),
)

try:
    import captcha
    urlpatterns += patterns('',
        url(r'^captcha/', include('captcha.urls')),
    )
except ImportError:
    pass

urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True)
