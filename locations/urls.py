from django.conf.urls.defaults import *

urlpatterns = patterns('locations.views',
    url(r'^(?P<loc_id>\d+)$', 'location_view', name='location_info', kwargs={'view': 'location_info', 'name': 'main'}),
    url(r'^(?P<loc_id>\d+)/wall$', 'location_view', name='location_wall', kwargs={'view': 'location_wall', 'name': 'main'}),
    url(r'^(?P<loc_id>\d+)/map$', 'location_view', name='location_map', kwargs={'view': 'location_map', 'name': 'main'}),
    url(r'^(?P<loc_id>\d+)/help$', 'location_view', name='location_help', kwargs={'view': 'location_help', 'name': 'main'}),
    url(r'^(?P<loc_id>\d+)/register$', 'location_register', name='location_register', kwargs={'view': 'location_register', 'name': 'main'}),

    url(r'^get_sub_regions$', 'get_sub_regions', name='get_sub_regions'),
    url(r'^goto_location$', 'goto_location', name='goto_location'),

    url(r'^map_data$', 'map_data', name='map_data'),
)
