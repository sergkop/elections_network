from django.conf.urls.defaults import *

urlpatterns = patterns('users.views',
    url(r'^profile$', 'profile', name='profile'),
    url(r'^login$', 'login', name='login'),
)
