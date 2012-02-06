# coding=utf8
import json

from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.template.response import TemplateResponse

from loginza.models import Identity, UserMap
from loginza.templatetags.loginza_widget import _return_path

from registration.forms import CompleteRegistrationForm, RegistrationForm
from registration.models import ActivationProfile
import registration.signals

def register(request):
    if request.user.is_authenticated():
        return redirect('edit_profile')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            #user = auth.authenticate(username=username, password=password)
            #assert user and user.is_authenticated()
            #auth.login(request, user)

            return redirect('registration_completed')
    else:
        form = RegistrationForm()

    return TemplateResponse(request, 'registration/register.html', {'form': form})

def registration_completed(request):
    if request.user.is_authenticated():
        return redirect('my_profile')
    return TemplateResponse(request, 'registration/registration_completed.html')

def activate(request, activation_key):
    account = ActivationProfile.objects.activate_user(activation_key)
    if account:
        return redirect('activation_completed')

    return TemplateResponse(request, 'registration/activation_fail.html')

def activation_completed(request):
    if request.user.is_authenticated():
        return redirect('my_profile')
    return TemplateResponse(request, 'registration/activation_completed.html')

# TODO: if username and email match an existing account - suggest to link them
def loginza_register(request):
    if request.user.is_authenticated():
        return redirect('my_profile')

    try:
        identity_id = request.session.get('users_complete_reg_id', None)
        user_map = UserMap.objects.select_related().get(identity__id=identity_id)
    except UserMap.DoesNotExist:
        return redirect('main')

    if request.method == 'POST':
        form = CompleteRegistrationForm(user_map.user.id, request.POST)
        if form.is_valid():
            user_map.user.username = form.cleaned_data['username']
            user_map.user.email = form.cleaned_data['email']
            user_map.user.first_name = form.cleaned_data['first_name']
            user_map.user.last_name = form.cleaned_data['last_name']
            user_map.user.set_password(form.cleaned_data["password1"])
            user_map.user.save()

            user_map.verified = True
            user_map.save()

            user = auth.authenticate(user_map=user_map)
            auth.login(request, user)

            messages.info(request, u'Добро пожаловать!')
            del request.session['users_complete_reg_id']
            return redirect(_return_path(request))
    else:
        form = CompleteRegistrationForm(user_map.user.id, initial={
                'username': user_map.user.username,
                'email': user_map.user.email,
        })

    user_map = UserMap.objects.get(user=user_map.user) # TODO: what if there are several user maps?
    data = json.loads(user_map.identity.data)
    form.initial['first_name'] = data['name']['first_name']
    form.initial['last_name'] = data['name']['last_name']

    return render_to_response('registration/loginza_register.html', {'form': form},
            context_instance=RequestContext(request))
