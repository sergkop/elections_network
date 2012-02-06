from django.conf.urls.defaults import *

urlpatterns = patterns('navigation.views',
    url(r'^$', 'main', name='main'),
    url(r'^map_search$', 'map_search', name='map_search'),
    url(r'^development$', 'development', name='development'),

    # Static pages
    url(r'^about$', 'static_page', {'name': 'about', 'template': 'static_pages/about.html'}, name='about'),
    url(r'^partners$', 'static_page', {'name': 'partners', 'template': 'static_pages/partners.html'}, name='partners'),
    url(r'^how_to_help$', 'static_page', {'name': 'how_to_help', 'template': 'static_pages/how_to_help.html'}, name='how_to_help'),
    url(r'^contacts$', 'static_page', {'name': 'contacts', 'template': 'static_pages/contacts.html'}, name='contacts'),
    url(r'^rules$', 'static_page', {'name': 'rules', 'template': 'static_pages/rules.html'}, name='rules'),
)

urlpatterns += patterns('',
    url(r'^get_sub_regions$', 'locations.views.get_sub_regions', name='get_sub_regions'),
    url(r'^goto_location$', 'locations.views.goto_location', name='goto_location'),
)
