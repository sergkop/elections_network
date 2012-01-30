# coding=utf8
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse

from links.models import Link
from reports.models import LINK_REPORT_TYPES, ReportLink, ReportUser, USER_REPORT_TYPES

def report_link(request):
    if request.method=='POST' and request.user.is_authenticated():
        try:
            location_id = int(request.POST.get('location', ''))
        except ValueError:
            return HttpResponse(u'Регион не найден')

        try:
            link = Link.objects.get(url=request.POST.get('report_link_radio', ''), location__id=location_id)
        except Link.DoesNotExist:
            return HttpResponse(u'Ссылка не найдена')

        reason = request.POST.get('reason')
        if reason not in LINK_REPORT_TYPES:
            return HttpResponse(u'Неправильно выбрана причина жалобы')

        if reason == 'other':
            reason_explained = request.POST.get('reason_explained', '')
            if reason_explained == '':
                return HttpResponse(u'Укажите причину жалобы')
        else:
            reason_explained = ''

        try:
            ReportLink.objects.create(link=link, user=request.user,
                    reason=reason, reason_explained=reason_explained)
        except IntegrityError:
            return HttpResponse('Вы уже пожаловались на эту ссылку')

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
