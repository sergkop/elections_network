from django.conf.urls.defaults import *

urlpatterns = patterns('merge.views',
    url(r'^$', 'main', name='main'),
    url(r'^(.*)/$', 'region', name='region'),
)
