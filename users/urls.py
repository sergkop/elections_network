from django.conf.urls.defaults import *
from django.views.generic.base import TemplateView
from users.views import JournalistSignupView, LawyerSignupView, MemberSignupView, \
    ObserverSignupView, ProsecutorSignupView, VoterSignupView


urlpatterns = patterns('users.views',
    url(r'^become_voter$', VoterSignupView.as_view(), name='become_voter'),
    url(r'^become_observer$', ObserverSignupView.as_view(), name='become_observer'),
    url(r'^become_journalist$', JournalistSignupView.as_view(), name='become_journalist'),
    url(r'^become_lawyer$', LawyerSignupView.as_view(), name='become_lawyer'),
    url(r'^become_prosecutor$', ProsecutorSignupView.as_view(), name='become_prosecutor'),
    url(r'^become_member$', MemberSignupView.as_view(), name='become_member'),

    url(r'^add_commission_member$', 'add_commission_member', name='add_commission_member'),
    url(r'^become_web_observer$', 'become_web_observer', name='become_web_observer'),

    url(r'^add_to_contacts$', 'add_to_contacts', name='add_to_contacts'),
    url(r'^remove_from_contacts$', 'remove_from_contacts', name='remove_from_contacts'),
    url(r'^send_message$', 'send_message', name='send_message'),

    url(r'^feedback/$', 'feedback', name='feedback'),
    url(r'^feedback/thanks/$', TemplateView.as_view(template_name='feedback/thanks.html'), name='feedback_thanks'),
    url(r'^feedback/fail/$', TemplateView.as_view(template_name='feedback/fail.html'), name='feedback_fail')
)
