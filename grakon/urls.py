from django.conf.urls.defaults import patterns, url
from django.contrib.auth import views as auth_views

from grakon.forms import LoginForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm

urlpatterns = patterns('grakon.views',
    url(r'^profile$', 'my_profile', name='my_profile'),
    url(r'^profile/edit$', 'edit_profile', name='edit_profile'),
    url(r'^user/(?P<username>\w+)$', 'profile', name='profile'),

    url(r'^logout$', 'logout', name='logout'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login$', 'login', name='login', kwargs={
            'template_name': 'auth/login.html', 'authentication_form': LoginForm}),

    # The two-step password change
    url(r'^change_password$', 'password_change', name='password_change', kwargs={
            'template_name': 'auth/password_change.html', 'password_change_form': PasswordChangeForm}),
    url(r'^password_change_done$', 'password_change_done', name='password_change_done', kwargs={
            'template_name': 'auth/password_change_done.html'}),

    # The four-step password reset
    url(r'^password_reset$', 'password_reset', name='password_reset', kwargs={
            'template_name': 'auth/password_reset.html', 'password_reset_form': PasswordResetForm}),
    url(r'^password_reset_complete$', 'password_reset_complete', name='password_reset_complete'),
    url(r'^password_reset_done$', 'password_reset_done', name='password_reset_done', kwargs={
            'template_name': 'auth/password_reset_done.html'}),
    url(r'^password_reset_confirm/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            'password_reset_confirm', name='password_reset_confirm', kwargs={'set_password_form': SetPasswordForm}),
)

from django.views.generic.base import TemplateView

urlpatterns += patterns('grakon.views',
    url(r'^auth/password_change_forbidden/$', TemplateView.as_view(template_name='registration/password_change_forbidden.html'),
        name='password_change_forbidden')
)
