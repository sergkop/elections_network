from django.conf.urls.defaults import *

urlpatterns = patterns('violations.views',
    url(r'^(?P<violation_id>\d+)$', 'violation_view', name='violation_view'),
    url(r'^(?P<violation_id>\d+)/edit$', 'violation_edit', name='violation_edit'),
    url(r'^report$', 'report_violation', name='report_violation'),
)
