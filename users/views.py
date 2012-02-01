# coding=utf8
from smtplib import SMTPException

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext

from locations.models import Location
from links.models import Link
from users.models import Contact, Role

def current_profile(request):
    """ Show profile of the currently logged in user """
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))
    return profile(request, request.user.username)

def profile(request, username):
    user = get_object_or_404(User, username=username)

    activities = {}
    for role in Role.objects.filter(user=user).select_related():
        activities[role.type] = {'user': role.user, 'location': role.location}

    context = {
        'profile_user': user,
        'profile': user.get_profile(),
        'activities': activities,
        'locations': list(Location.objects.filter(parent_1=None).order_by('name')),
        'links': list(Link.objects.filter(user=user).select_related()),
        'contacts': list(Contact.objects.filter(user=user)) if user.is_authenticated() else [],
        'have_in_contacts': list(Contact.objects.filter(contact=user)),
    }
    return render_to_response('users/profile.html', context_instance=RequestContext(request, context))

def become_voter(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        for name in ('region_3', 'region_2', 'region_1'):
            try:
                location_id = int(request.POST.get(name, ''))
            except ValueError:
                continue

            try:
                role, created = Role.objects.get_or_create(
                        type='voter', user=request.user, defaults={'location_id': location_id})
            except IntegrityError:
                return HttpResponse(u'Ошибка базы данных')

            if not created:
                role.location_id = location_id
                role.save()

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
