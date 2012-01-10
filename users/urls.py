from django.conf.urls.defaults import *

urlpatterns = patterns('users.views',
    url(r'^$', 'current_profile', name='current_profile'),
    url(r'^(\w+)/$', 'profile', name='profile'),
)
