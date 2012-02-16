from django.conf.urls.defaults import *

from users.views import ObserverSignupView, VoterSignupView

urlpatterns = patterns('users.views',
    url(r'^become_voter$', VoterSignupView.as_view(), name='become_voter'),
    url(r'^become_observer$', ObserverSignupView.as_view(), name='become_observer'),

    url(r'^add_to_contacts$', 'add_to_contacts', name='add_to_contacts'),
    url(r'^remove_from_contacts$', 'remove_from_contacts', name='remove_from_contacts'),
    url(r'^send_message$', 'send_message', name='send_message'),
)
