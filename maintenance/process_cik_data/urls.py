from settings import MEDIA_ROOT
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    url(r'^', include('merge.urls')),
)
