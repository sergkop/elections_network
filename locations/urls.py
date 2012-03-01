from django.conf.urls.defaults import *

urlpatterns = patterns('locations.views',
    url(r'^(?P<loc_id>\d+)$', 'location_view', name='location_info', kwargs={'view': 'location_info'}),
    url(r'^(?P<loc_id>\d+)/wall$', 'location_view', name='location_wall', kwargs={'view': 'location_wall'}),
    url(r'^(?P<loc_id>\d+)/map$', 'location_view', name='location_map', kwargs={'view': 'location_map'}),
    url(r'^(?P<loc_id>\d+)/web_observers', 'location_view', name='web_observers', kwargs={'view': 'web_observers'}),
    url(r'^(?P<loc_id>\d+)/supporters', 'location_view', name='supporters', kwargs={'view': 'supporters'}),

    url(r'^get_sub_regions$', 'get_sub_regions', name='get_sub_regions'),
    url(r'^goto_location$', 'goto_location', name='goto_location'),

    url(r'^locations_data$', 'locations_data', name='locations_data'),
)
