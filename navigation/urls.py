from django.conf.urls.defaults import patterns, url

def tabbed_static_url(name, template):
    return url(r'^'+name+'$', 'static_page', {'name': name, 'template': template}, name=name)

urlpatterns = patterns('navigation.views',
    url(r'^$', 'main', {'tab': 'main'}, name='main'),
    url(r'^wall$', 'wall', {'tab': 'wall'}, name='wall'),

    url(r'^uik_search$', 'uik_search', name='uik_search'),
    url(r'^uik_search_data$', 'uik_search_data', name='uik_search_data'),

    # Static pages
    tabbed_static_url('about', 'static_pages/about/base.html'),
    tabbed_static_url('rules', 'static_pages/about/base.html'),
	tabbed_static_url('comparison', 'static_pages/about/base.html'),
	tabbed_static_url('publications', 'static_pages/about/base.html'),

    tabbed_static_url('news', 'static_pages/development/base.html'),
    tabbed_static_url('functionality', 'static_pages/development/base.html'),

    tabbed_static_url('join_team', 'static_pages/how_to_help/base.html'),
    tabbed_static_url('donate', 'static_pages/how_to_help/base.html'),
    tabbed_static_url('volunteer', 'static_pages/how_to_help/base.html'),
    tabbed_static_url('share', 'static_pages/how_to_help/base.html'),
#    tabbed_static_url('feedback', 'static_pages/how_to_help/base.html'),

    url(r'^partners$', 'static_page', {'name': 'partners', 'template': 'static_pages/partners.html'}, name='partners'),
	url(r'^faq$', 'static_page', {'name': 'faq', 'template': 'static_pages/faq.html'}, name='faq'),

    url(r'^sitemap$', 'sitemap', name='sitemap'),
)
