# coding=utf8
import json
from smtplib import SMTPException

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

from geography.models import Location
from links.models import Link
from users.forms import CompleteRegistrationForm
from users.models import Contact, Participation, ReportUser, USER_REPORT_TYPES
import users.signals

def current_profile(request):
    """ Show profile of the currently logged in user """
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))
    return profile(request, request.user.username)

def profile(request, username):
    user = get_object_or_404(User, username=username)

    activities = {}
    for participation in Participation.objects.filter(user=user).select_related():
        activities[participation.type] = {'user': participation.user, 'location': participation.location}

    context = {
        'profile_user': user,
        'profile': user.get_profile(),
        'activities': activities,
        'locations': list(Location.objects.filter(parent_1=None).order_by('name')),
        'links': list(Link.objects.filter(user=user).select_related()),
        'contacts': list(Contact.objects.filter(user=user)) if user.is_authenticated() else [],
        'have_in_contacts': list(Contact.objects.filter(contact=user)),
    }
    return render_to_response('profile.html', context_instance=RequestContext(request, context))

def become_voter(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        for name in ('region_3', 'region_2', 'region_1'):
            try:
                location_id = int(request.POST.get(name, ''))
            except ValueError:
                continue

            try:
                participation, created = Participation.objects.get_or_create(
                        type='voter', user=request.user, defaults={'location_id': location_id})
            except IntegrityError:
                return HttpResponse(u'Ошибка базы данных')

            if not created:
                participation.location_id = location_id
                participation.save()

            return HttpResponse('ok')

    return HttpResponse(u'Ошибка')

def add_to_contacts(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        try:
            contact = User.objects.get(username=request.POST.get('username', ''))
        except User.DoesNotExist:
            return HttpResponse(u'Пользователь не существует')

        try:
            Contact.objects.create(user=request.user, contact=contact)
        except IntegrityError:
            return HttpResponse(u'Пользователь уже добавлен в контакты')

        return HttpResponse('ok')

    return HttpResponse(u'Ошибка')

def remove_from_contacts(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        try:
            contact = User.objects.get(username=request.POST.get('username', ''))
        except User.DoesNotExist:
            return HttpResponse(u'Пользователь не существует')

        Contact.objects.filter(user=request.user, contact=contact).delete()
        return HttpResponse('ok')

    return HttpResponse(u'Ошибка')

def report_user(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        try:
            user = User.objects.get(username=request.POST.get('username', ''))
        except User.DoesNotExist:
            return HttpResponse(u'Пользователь не существует')

        reason = request.POST.get('reason')
        if reason not in USER_REPORT_TYPES:
            return HttpResponse(u'Неправильно выбрана причина жалобы')

        if reason == 'other':
            reason_explained = request.POST.get('reason_explained', '')
            if reason_explained == '':
                return HttpResponse(u'Укажите причину жалобы')
        else:
            reason_explained = ''

        try:
            report = ReportUser.objects.create(user=user, reporter=request.user,
                    reason=reason, reason_explained=reason_explained)
        except IntegrityError:
            return HttpResponse(u'Вы уже пожаловались на этого пользователя')

        return HttpResponse('ok')

    return HttpResponse(u'Ошибка')

def send_message(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        try:
            user = User.objects.get(username=request.POST.get('username', ''))
        except User.DoesNotExist:
            return HttpResponse(u'Пользователь не существует')

        title = request.POST.get('message_title', '')
        if title == '':
            return HttpResponse(u'Введите тему сообщения')

        message_body = request.POST.get('message_body', '')
        if message_body == '':
            return HttpResponse(u'Введите текст сообщения')

        try:
            send_mail(title, message_body, request.user.email, [user.email], fail_silently=False)
        except SMTPException:
            return HttpResponse(u'Не удалось отправить сообщение')

        return HttpResponse('ok')

    return HttpResponse(u'Ошибка')

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
