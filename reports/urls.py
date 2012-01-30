from django.conf.urls.defaults import *

urlpatterns = patterns('reports.views',
    url(r'^report_link$', 'report_link', name='report_link'),
    url(r'^report_user$', 'report_user', name='report_user'),
)