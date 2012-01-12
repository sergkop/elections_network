# -*- coding:utf-8 -*-
import json

from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext

from loginza.models import Identity, UserMap
from loginza.templatetags.loginza_widget import _return_path

from links.models import LinkModel
from users.forms import CompleteRegistrationForm
from users.models import ParticipationModel
import users.signals

def current_profile(request):
    """ Show profile of the currently logged in user """
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))
    return profile(request, request.user.username)

def profile(request, username):
    current_user = (request.user.username==username)

    user = get_object_or_404(User, username=username)

    context = {
        'profile_user': user,
        'participations': list(ParticipationModel.objects.filter(user=user).select_related()),
        'links': list(LinkModel.objects.filter(user=user).select_related()),
    }
    return render_to_response('profile.html', context_instance=RequestContext(request, context))

# TODO: if username and email match an existing account - suggest to link them
def complete_registration(request):
    if request.user.is_authenticated():
        return HttpResponseForbidden(u'Вы попали сюда по ошибке') # TODO: redirect

    try:
        identity_id = request.session.get('users_complete_reg_id', None)
        user_map = UserMap.objects.select_related().get(identity__id=identity_id)
    except UserMap.DoesNotExist:
        return HttpResponseForbidden(u'Вы попали сюда по ошибке')

    if request.method == 'POST':
        form = CompleteRegistrationForm(user_map.user.id, request.POST)
        if form.is_valid():
            user_map.user.username = form.cleaned_data['username']
            user_map.user.email = form.cleaned_data['email']
            user_map.user.first_name = form.cleaned_data['first_name']
            user_map.user.last_name = form.cleaned_data['last_name']
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

    return render_to_response('complete_registration.html', {'form': form},
            context_instance=RequestContext(request))
