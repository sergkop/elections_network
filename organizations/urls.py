from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('organizations.views',
    url(r'^(?P<name>[\w\.]+)$', 'organization_info', name='organization_info'),
    url(r'^(?P<name>[\w\.]+)/edit$', 'edit_organization', name='edit_organization'),
    url(r'^/create$', 'create_organization', name='create_organization'),
)
