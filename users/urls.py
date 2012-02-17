from django.conf.urls.defaults import *

from users.views import JournalistSignupView, LawyerSignupView, ObserverSignupView, \
        ProsecutorSignupView, VoterSignupView

urlpatterns = patterns('users.views',
    url(r'^become_voter$', VoterSignupView.as_view(), name='become_voter'),
    url(r'^become_observer$', ObserverSignupView.as_view(), name='become_observer'),
    url(r'^become_journalist$', JournalistSignupView.as_view(), name='become_journalist'),
    url(r'^become_lawyer$', LawyerSignupView.as_view(), name='become_lawyer'),
    url(r'^become_prosecutor$', ProsecutorSignupView.as_view(), name='become_prosecutor'),

    url(r'^add_to_contacts$', 'add_to_contacts', name='add_to_contacts'),
    url(r'^remove_from_contacts$', 'remove_from_contacts', name='remove_from_contacts'),
    url(r'^send_message$', 'send_message', name='send_message'),
)
