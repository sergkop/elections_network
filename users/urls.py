from django.conf.urls.defaults import url, patterns

from users.views import ProfileUpdateView

urlpatterns = patterns('users.views',
    url(r'^$', 'current_profile', name='current_profile'),
    url(r'^update/$', ProfileUpdateView.as_view(), name='update_profile'),
    url(r'^(\w+)/$', 'profile', name='profile'),
)
