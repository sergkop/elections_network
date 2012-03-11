from django.conf.urls.defaults import *

from locations.views import *

urlpatterns = patterns('locations.views',
    url(r'^(?P<loc_id>\d+)$', InfoView.as_view(), name='location_info', kwargs={'view': 'location_info'}),
    url(r'^(?P<loc_id>\d+)/wall$', 'location_view', name='location_wall', kwargs={'view': 'location_wall'}),
    url(r'^(?P<loc_id>\d+)/map$', 'location_view', name='location_map', kwargs={'view': 'location_map'}),
    url(r'^(?P<loc_id>\d+)/web_observers', WebObserversView.as_view(), name='web_observers', kwargs={'view': 'web_observers'}),
    url(r'^(?P<loc_id>\d+)/participants', ParticipantsView.as_view(), name='participants', kwargs={'view': 'participants'}),
    url(r'^(?P<loc_id>\d+)/violations', ViolationsView.as_view(), name='violations', kwargs={'view': 'violations'}),
    url(r'^(?P<loc_id>\d+)/protocols', ProtocolsView.as_view(), name='protocols', kwargs={'view': 'protocols'}),
    url(r'^(?P<loc_id>\d+)/links', LinksView.as_view(), name='links', kwargs={'view': 'links'}),
    url(r'^(?P<loc_id>\d+)/organizations', OrganizationsView.as_view(), name='organizations', kwargs={'view': 'organizations'}),

    # Redirect, not used anymore
    url(r'^(?P<loc_id>\d+)/supporters', 'location_supporters', name='supporters'),

    url(r'^get_sub_regions$', 'get_sub_regions', name='get_sub_regions'),
    url(r'^goto_location$', 'goto_location', name='goto_location'),

    url(r'^locations_data$', 'locations_data', name='locations_data'),
)
