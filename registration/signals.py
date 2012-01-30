from django.contrib import messages, auth
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from loginza import signals, models

def loginza_error_handler(sender, error, **kwargs):
    messages.error(sender, error.message)

signals.error.connect(loginza_error_handler)

def loginza_auth_handler(sender, user, identity, **kwargs):
    try:
        # it's enough to have single identity verified to treat user as verified
        models.UserMap.objects.get(user=user, verified=True)
        auth.login(sender, user)
    except models.UserMap.DoesNotExist:
        sender.session['users_complete_reg_id'] = identity.id
        return redirect(reverse('loginza_register'))

signals.authenticated.connect(loginza_auth_handler)

def loginza_login_required(sender, **kwargs):
    messages.warning(sender, u'Function is only available to authorized users')

signals.login_required.connect(loginza_login_required)
