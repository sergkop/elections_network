from django.conf.urls.defaults import *

urlpatterns = patterns('search.views',
    url(r'^search$', 'user_list', name='user_list'),
    url(r'^search/table$', 'user_table', name='user_table'),
    url(r'^search/map$', 'map', name='map'),
)
