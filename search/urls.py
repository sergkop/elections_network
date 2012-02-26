from django.conf.urls.defaults import *

urlpatterns = patterns('search.views',
    url(r'^search$', 'user_list', name='user_list'),
    url(r'^search/table$', 'user_table', name='user_table'),
    url(r'^search/map$', 'map', name='map'),
    url(r'^find_uik$', 'find_uik', name='find_uik'),
    url(r'^uik_search_data$', 'uik_search_data', name='uik_search_data'),
)
