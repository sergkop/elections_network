from django.conf.urls.defaults import patterns, url

def tabbed_static_url(name, template):
    return url(r'^'+name+'$', 'static_page', {'name': name, 'template': template, 'tab': name}, name=name)

urlpatterns = patterns('navigation.views',
    url(r'^$', 'main', name='main'),
    url(r'^map_search$', 'map_search', name='map_search'),

    # Static pages
    tabbed_static_url('about', 'static_pages/about/base.html'),
    tabbed_static_url('rules', 'static_pages/about/base.html'),

    tabbed_static_url('news', 'static_pages/development/base.html'),
    tabbed_static_url('functionality', 'static_pages/development/base.html'),

    url(r'^partners$', 'static_page', {'name': 'partners', 'template': 'static_pages/partners.html'}, name='partners'),
    url(r'^how_to_help$', 'static_page', {'name': 'how_to_help', 'template': 'static_pages/how_to_help.html'}, name='how_to_help'),
    url(r'^contacts$', 'static_page', {'name': 'contacts', 'template': 'static_pages/contacts.html'}, name='contacts'),
)
