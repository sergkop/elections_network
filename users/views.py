import json

from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext

from loginza.models import Identity, UserMap
from loginza.templatetags.loginza_widget import _return_path

from users.forms import CompleteRegistrationForm
from users.models import ParticipationModel
import users.signals

def current_profile(request):
    """ Show profile of the currently logged in user """
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    context = {
        'user': request.user,
        'participations': list(ParticipationModel.objects.filter(user=request.user).select_related()),
    }
    return render_to_response('profile.html', context_instance=RequestContext(request, context))

def profile(request, username):
    if request.user.username == username:
        return current_profile(request)

    user = get_object_or_404(User, username=username)

    context = {
        'user': user,
        'participations': list(ParticipationModel.objects.filter(user=user).select_related()),
    }
    return render_to_response('profile.html', context_instance=RequestContext(request, context))

def complete_registration(request):
    if request.user.is_authenticated():
        return HttpResponseForbidden('sdfsd') # TODO: redirect

    try:
        identity_id = request.session.get('users_complete_reg_id', None)
        user_map = UserMap.objects.get(identity__id=identity_id)
    except UserMap.DoesNotExist:
        return HttpResponseForbidden('sdf')

    if request.method == 'POST':
        form = CompleteRegistrationForm(user_map.user.id, request.POST)
        if form.is_valid():
            user_map.user.username = form.cleaned_data['username']
            user_map.user.email = form.cleaned_data['email']
            user_map.user.save()

            user_map.verified = True
            user_map.save()

            user = auth.authenticate(user_map=user_map)
            auth.login(request, user)

            messages.info(request, u'Welcome!')
            del request.session['users_complete_reg_id']
            return redirect(_return_path(request))
    else:
        form = CompleteRegistrationForm(user_map.user.id, initial={
                'username': user_map.user.username,
                'email': user_map.user.email,
        })

    return render_to_response('register.html', {'form': form},
            context_instance=RequestContext(request))
