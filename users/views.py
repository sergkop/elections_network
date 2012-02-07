# coding=utf8
from smtplib import SMTPException

from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import HttpResponse

from grakon.models import Profile
from users.models import Contact, Role

def become_voter(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        for name in ('region_3', 'region_2', 'region_1'):
            try:
                location_id = int(request.POST.get(name, ''))
            except ValueError:
                continue

            try:
                role, created = Role.objects.get_or_create(
                        type='voter', user=request.user.get_profile(), defaults={'location_id': location_id})
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
            contact = Profile.objects.get(username=request.POST.get('username', ''))
        except Profile.DoesNotExist:
            return HttpResponse(u'Пользователь не существует')

        try:
            Contact.objects.create(user=request.user.get_profile(), contact=contact)
        except IntegrityError:
            return HttpResponse(u'Пользователь уже добавлен в контакты')

        return HttpResponse('ok')

    return HttpResponse(u'Ошибка')

def remove_from_contacts(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        try:
            contact = Profile.objects.get(username=request.POST.get('username', ''))
        except Profile.DoesNotExist:
            return HttpResponse(u'Пользователь не существует')

        Contact.objects.filter(user=request.user.get_profile(), contact=contact).delete()
        return HttpResponse('ok')

    return HttpResponse(u'Ошибка')

def send_message(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        try:
            profile = Profile.objects.get(username=request.POST.get('username', ''))
        except Profile.DoesNotExist:
            return HttpResponse(u'Пользователь не существует')

        title = request.POST.get('message_title', '')
        if title == '':
            return HttpResponse(u'Введите тему сообщения')

        message_body = request.POST.get('message_body', '')
        if message_body == '':
            return HttpResponse(u'Введите текст сообщения')

        try:
            send_mail(title, message_body, request.user.email, [profile.user.email], fail_silently=False)
        except SMTPException:
            return HttpResponse(u'Не удалось отправить сообщение')

        return HttpResponse('ok')

    return HttpResponse(u'Ошибка')
