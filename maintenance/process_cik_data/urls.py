from django.conf.urls.defaults import patterns, include, url

from settings import MEDIA_ROOT

urlpatterns = patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    url(r'^', include('merge.urls')),
)
