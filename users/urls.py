from django.conf.urls.defaults import *

urlpatterns = patterns('users.views',
    url(r'^become_voter$', 'become_voter', name='become_voter'),
    url(r'^add_to_contacts$', 'add_to_contacts', name='add_to_contacts'),
    url(r'^remove_from_contacts$', 'remove_from_contacts', name='remove_from_contacts'),
    url(r'^send_message$', 'send_message', name='send_message'),
)
