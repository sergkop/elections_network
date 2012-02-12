from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('organizations.views',
    url(r'^organization/(?P<name>[\w\.]+)$', 'organization_view', name='organization_info', kwargs={'view': 'organization_info'}),
)
