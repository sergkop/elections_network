from django.contrib import messages, auth
from django.core.urlresolvers import reverse
from django.dispatch.dispatcher import receiver
from django.shortcuts import redirect

from loginza import signals, models

@receiver(signals.error)
def loginza_error_handler(sender, error, **kwargs):
    messages.error(sender, error.message)

@receiver(signals.authenticated)
def loginza_auth_handler(sender, user, identity, **kwargs):
    try:
        # it's enough to have single identity verified to treat user as verified
        models.UserMap.objects.get(user=user, verified=True)
        auth.login(sender, user)
    except models.UserMap.DoesNotExist:
        sender.session['users_complete_reg_id'] = identity.id
        return redirect(reverse('loginza_register'))
    """
    request = sender
    try:
        UserMap.objects.get(user=user)
        user.grakonprofile.update_from_identity(identity)
        auth.login(request, user)
        return redirect('EditProfile')
    except UserMap.DoesNotExist:
        return redirect('Login')
    """

@receiver(signals.login_required)
def loginza_login_required(sender, **kwargs):
    messages.warning(sender, u'Function is only available to authorized users')
