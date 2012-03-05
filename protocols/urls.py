from django.conf.urls.defaults import *

urlpatterns = patterns('protocols.views',
    url(r'^(?P<protocol_id>\d+)$', 'protocol_view', name='protocol_view'),
)
