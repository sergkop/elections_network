# coding=utf8
import json

from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.template.response import TemplateResponse

from loginza.models import UserMap
from loginza.templatetags.loginza_widget import _return_path

from grakon.utils import authenticated_redirect
from registration.forms import LoginzaRegistrationForm, RegistrationForm
from registration.models import ActivationProfile
import registration.signals

@authenticated_redirect('edit_profile')
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            return redirect('registration_completed')
    else:
        form = RegistrationForm()

    return TemplateResponse(request, 'registration/register.html', {'form': form})

@authenticated_redirect('my_profile')
def registration_completed(request):
    return TemplateResponse(request, 'registration/registration_completed.html')

@authenticated_redirect('my_profile')
def activate(request, activation_key):
    account = ActivationProfile.objects.activate_user(activation_key)
    if account:
        return redirect('activation_completed')
    return TemplateResponse(request, 'registration/activation_fail.html')

@authenticated_redirect('my_profile')
def activation_completed(request):
    return TemplateResponse(request, 'registration/activation_completed.html')

# TODO: if username and email match an existing account - suggest to link them
# TODO: if there is a need to delete user, registered with loginza - identity must be removed as well
# TODO: what if there are several user maps?
# TODO: indicate if activation email is already sent
@authenticated_redirect('my_profile')
def loginza_register(request):
    try:
        identity_id = request.session.get('users_complete_reg_id', None)
        user_map = UserMap.objects.select_related().get(identity__id=identity_id)
    except UserMap.DoesNotExist:
        return redirect('login')

    user_data = json.loads(user_map.identity.data)

    if request.method == 'POST':
        form = LoginzaRegistrationForm(request.POST, user_map=user_map)
        if form.is_valid():
            user = form.save()

            # check if email if provided by loginza - no need to verify it then
            if user_data.get('email') == user.email: # no need to confirm email
                user = auth.authenticate(username=user.username, password=form.cleaned_data.get('password1',''))
                assert user and user.is_authenticated()
                auth.login(request, user)

                #messages.info(request, u'Добро пожаловать!')
                del request.session['users_complete_reg_id']
                return redirect(_return_path(request))
            else:
                return redirect('registration_completed')
    else:
        form = LoginzaRegistrationForm(user_map=user_map, initial={
                'email': user_map.user.email,
        })

    if 'name' in user_data:
        form.initial['first_name'] = user_data['name'].get('first_name', '')
        form.initial['last_name'] = user_data['name'].get('last_name', '')

    return render_to_response('registration/loginza_register.html', {'form': form},
            context_instance=RequestContext(request))
