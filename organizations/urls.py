from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('organizations.views',
    url(r'^organization/(?P<name>[\w\.]+)$', 'organization_info', name='organization_info'),
    url(r'^organization/(?P<name>[\w\.]+)/edit$', 'edit_organization', name='edit_organization'),
    url(r'^create_organization$', 'create_organization', name='create_organization'),
)
