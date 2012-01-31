from django.conf.urls.defaults import *

urlpatterns = patterns('reports.views',
    url(r'^report$', 'report', name='report'),
)