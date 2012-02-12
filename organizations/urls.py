from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('organizations.views',
    url(r'^organization/(?P<name>[\w\.]+)$', 'organization', name='organization'),
)
