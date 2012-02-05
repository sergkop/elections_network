from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    url(r'^loginza_register$', 'registration.views.loginza_register', name='loginza_register'),
    url(r'^register/complete/$', direct_to_template, {'template': 'users/registration_complete.html'},
            name='registration_complete'),

    url(r'^register$', 'registration.views.register', name='register'),

    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$', 'registration.views.activate', name='registration_activate'),
    url(r'^activate/complete/$', direct_to_template, {'template': 'users/activation_complete.html'},
            name='registration_activation_complete'),
)
