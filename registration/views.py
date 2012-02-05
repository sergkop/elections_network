# coding=utf8
import json

from django.contrib import messages, auth
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from loginza.models import Identity, UserMap
from loginza.templatetags.loginza_widget import _return_path

from registration.forms import CompleteRegistrationForm, RegistrationForm
from registration.models import RegistrationProfile
import registration.signals

# TODO: what happens on /login page? login.html is a duplicate for elements/login.html
def login(request):
    if request.user.is_authenticated():
        return redirect('my_profile')
    return auth_views.login(request, template_name='users/login.html')

def logout(request):
    next_page = reverse('main') if 'next' in request.REQUEST else None
    return auth_views.logout(request, next_page)

# TODO: add captcha (?)
def register(request):
    if request.user.is_authenticated():
        return redirect('my_profile')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            #new_user = RegistrationProfile.objects.create_inactive_user(username, email, password)
            #return redirect('registration_complete')

            user = User.objects.create_user(username, form.cleaned_data['email'], password)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            user = auth.authenticate(username=username, password=password)

            assert user and user.is_authenticated()
            auth.login(request, user)

            # TODO: redirect to a message with confirmation
            return redirect(user.get_absolute_url())

    else:
        form = RegistrationForm()

    return render_to_response('users/register.html',
            context_instance=RequestContext(request, {'form': form}))

def activate(request, activation_key):
    account = RegistrationProfile.objects.activate_user(activation_key)
    if account:
        return redirect('registration_activation_complete')

    return render_to_response('users/activate.html', context_instance=RequestContext(request, kwargs))

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

    return render_to_response('users/loginza_register.html', {'form': form},
            context_instance=RequestContext(request))
