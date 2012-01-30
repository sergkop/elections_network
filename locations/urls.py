from django.conf.urls.defaults import *

urlpatterns = patterns('locations.views',
    url(r'^(\d+)$', 'location', name='location'),
)
