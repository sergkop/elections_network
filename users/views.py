# -*- coding:utf-8 -*-
import json

from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext

from loginza.models import Identity, UserMap
from loginza.templatetags.loginza_widget import _return_path

from links.models import LinkModel
from users.forms import CompleteRegistrationForm
from users.models import ContactModel, ParticipationModel, ReportUserModel
import users.signals

def current_profile(request):
    """ Show profile of the currently logged in user """
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))
    return profile(request, request.user.username)

def profile(request, username):
    user = get_object_or_404(User, username=username)

    if request.user.is_authenticated() and request.user.username!=username:
        in_contacts = ContactModel.objects.filter(user=request.user, contact=user).count()>0
        is_reported = ReportUserModel.objects.filter(user=user, reporter=request.user).count()>0
    else:
        in_contacts = False
        is_reported = False

    context = {
        'profile_user': user,
        'participations': list(ParticipationModel.objects.filter(user=user).select_related()),
        'links': list(LinkModel.objects.filter(user=user).select_related()),
        'in_contacts': in_contacts,
        'is_reported': is_reported,
        'contacts': list(ContactModel.objects.filter(user=user)),
        'have_in_contacts': list(ContactModel.objects.filter(contact=user)),
    }
    return render_to_response('profile.html', context_instance=RequestContext(request, context))

def become_voter(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        try:
            location_id = int(request.POST.get('region_1', ''))
        except ValueError:
            return HttpResponse('fail1')

        try:
            participation, created = ParticipationModel.objects.get_or_create(
                    type='voter', user=request.user, defaults={'location_id': location_id})
        except IntegrityError:
            return HttpResponse('fail2')

        if not created:
            participation.location_id = location_id
            participation.save()

        return HttpResponse('ok')

    return HttpResponse('fail3')

def add_to_contacts(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        try:
            contact = User.objects.get(username=request.POST.get('username', ''))
        except User.DoesNotExist:
            return HttpResponse('fail1')

        try:
            contact, created = ContactModel.objects.get_or_create(
                    user=request.user, contact=contact, defaults={})
        except IntegrityError:
            return HttpResponse('fail2')

        return HttpResponse('ok')

    return HttpResponse('fail3')

def report_user(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        try:
            user = User.objects.get(username=request.POST.get('username', ''))
        except User.DoesNotExist:
            return HttpResponse('fail1')

        try:
            report, created = ReportUserModel.objects.get_or_create(
                    user=user, reporter=request.user, defaults={})
        except IntegrityError:
            return HttpResponse('fail2')

        return HttpResponse('ok')

    return HttpResponse('fail3')

def send_message(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        try:
            user = User.objects.get(username=request.POST.get('username', ''))
        except User.DoesNotExist:
            return HttpResponse('fail1')

        try:
            send_mail(request.POST.get('message_title', ''), request.POST.get('message_body', ''),
                    request.user.email, [user.email], fail_silently=False)
        except: # TODO: explicit exception here
            return HttpResponse('fail2')

        return HttpResponse('ok')

    return HttpResponse('fail3')

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

    return render_to_response('complete_registration.html', {'form': form},
            context_instance=RequestContext(request))
