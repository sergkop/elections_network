from django.conf.urls.defaults import *

urlpatterns = patterns('navigation.views',
    url(r'^$', 'main', name='main'),

    # Static pages
    url(r'^about$', 'static_page', {'name': 'about', 'template': 'static_pages/about.html'}, name='about'),
    url(r'^partners$', 'static_page', {'name': 'partners', 'template': 'static_pages/partners.html'}, name='partners'),
    url(r'^help$', 'static_page', {'name': 'help', 'template': 'static_pages/help.html'}, name='help'),
    url(r'^contacts$', 'static_page', {'name': 'contacts', 'template': 'static_pages/contacts.html'}, name='contacts'),
)

urlpatterns += patterns('',
    url(r'^get_sub_regions$', 'locations.views.get_sub_regions', name='get_sub_regions'),
    url(r'^goto_location$', 'locations.views.goto_location', name='goto_location'),
)
