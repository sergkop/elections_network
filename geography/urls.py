from django.conf.urls.defaults import *

urlpatterns = patterns('geography.views',
    url(r'^(\d+)$', 'location', name='location'),
)
