from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views
from django.views.generic.simple import direct_to_template

from registration.views import activate, register

urlpatterns = patterns('',
    url(r'^login$', 'registration.views.login', name='login'),
    url(r'^logout$', 'registration.views.logout', name='logout'),
    url(r'^register$', 'registration.views.register', name='register'),

    url(r'^loginza_register$', 'registration.views.loginza_register', name='loginza_register'),
    url(r'^register/complete/$', direct_to_template, {'template': 'users/registration_complete.html'},
            name='registration_complete'),

    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$', 'registration.views.activate', name='registration_activate'),
    url(r'^activate/complete/$', direct_to_template, {'template': 'users/activation_complete.html'},
            name='registration_activation_complete'),

    # The two-step password change
    url(r'^password/change/$', auth_views.password_change, name='auth_password_change'),
    url(r'^password/change/done/$', auth_views.password_change_done, name='auth_password_change_done'),

    # The four-step password reset
    url(r'^password/reset/$', auth_views.password_reset, name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm,
            name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$', auth_views.password_reset_complete, name='auth_password_reset_complete'),
    url(r'^password/reset/done/$', auth_views.password_reset_done, name='auth_password_reset_done'),
)
