from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('registration.views',
    url(r'^loginza_register$', 'loginza_register', name='loginza_register'),

    url(r'^register$', 'register', name='register'),
    url(r'^registration_completed$', 'registration_completed', name='registration_completed'),

    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)$', 'activate', name='activate_account'),
    url(r'^activation_completed$', 'activation_completed', name='activation_completed'),
)
