from django.conf.urls.defaults import *

urlpatterns = patterns('links.views',
    url(r'^add_link$', 'add_link', name='add_link'),
)
