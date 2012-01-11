from django.conf.urls.defaults import *

urlpatterns = patterns('navigation.views',
    url(r'^$', 'main', name='main'),
    url(r'^login$', 'login', name='login'),
    url(r'^logout$', 'logout', name='logout'),
    url(r'^register$', 'register', name='register'),
)

urlpatterns += patterns('',
    url(r'^complete_registration$', 'users.views.complete_registration', name='complete_registration'),
)
