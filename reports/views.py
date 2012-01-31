# coding=utf8
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse

from links.models import Link
from reports.models import Report, REASON_TYPES

def report(request):
    if request.method=='POST' and request.user.is_authenticated():
        report_type = request.POST.get('type', '')
        if report_type not in CONTENT_TYPES:
            return HttpResponse(u'Тип жалобы указан неверно')

        if report_type == 'user':
            try:
                item = User.objects.get(username=request.POST.get('username', ''))
            except User.DoesNotExist:
                return HttpResponse(u'Пользователь не существует')

        elif report_type == 'link':
            try:
                location_id = int(request.POST.get('location', ''))
            except ValueError:
                return HttpResponse(u'Регион не найден')

            try:
                item = Link.objects.get(url=request.POST.get('report_link_radio', ''), location__id=location_id)
            except Link.DoesNotExist:
                return HttpResponse(u'Ссылка не найдена')

        else:
            return HttpResponse()

        reason = request.POST.get('reason')
        if reason not in REASON_TYPES[report_type]:
            return HttpResponse(u'Неправильно выбрана причина жалобы')

        if reason == 'other':
            reason_explained = request.POST.get('reason_explained', '')
            if reason_explained == '':
                return HttpResponse(u'Укажите причину жалобы')
        else:
            reason_explained = ''

        try:
            Report.objects.create(item=item, user=request.user,
                    reason=reason, reason_explained=reason_explained)
        except IntegrityError:
            return HttpResponse('Вы уже пожаловались на этот элемент')

        return HttpResponse('ok')

    return HttpResponse(u'Ошибка')
