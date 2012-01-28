# coding=utf8
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.http import HttpResponse

from links.models import Link, LINK_REPORT_TYPES, ReportLink

def add_link(request):
    if request.method=='POST' and request.user.is_authenticated():
        try:
            location_id = int(request.POST.get('location', ''))
        except ValueError:
            return HttpResponse(u'Регион не найден')

        name = request.POST.get('name', '')
        if name == '':
            return HttpResponse(u'Введите название ссылки')

        url = request.POST.get('url', '')
        try:
            URLValidator().__call__(url)
        except Exception, e:
            return HttpResponse(u'Неправильный формат url')

        try:
            Link.objects.create(location_id=location_id, user=request.user, url=url, name=name)
        except IntegrityError:
            return HttpResponse(u'Такая ссылка уже добавлена')

        return HttpResponse('ok')

    return HttpResponse(u'Ошибка')

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
