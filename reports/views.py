# coding=utf8
from django.db import IntegrityError
from django.http import HttpResponse

from grakon.models import Profile
from links.models import Link
from reports.models import Report, REASON_TYPES

def report(request):
    if request.method=='POST' and request.user.is_authenticated():
        report_type = request.POST.get('type', '')
        if report_type not in REASON_TYPES:
            return HttpResponse(u'Тип жалобы указан неверно')

        if report_type == 'user':
            try:
                item = Profile.objects.get(username=request.POST.get('username', ''))
            except Profile.DoesNotExist:
                return HttpResponse(u'Пользователь не существует')

            already_msg = u'Вы уже пожаловались на этого пользователя'

        elif report_type == 'link':
            try:
                location_id = int(request.POST.get('location', ''))
            except ValueError:
                return HttpResponse(u'Регион не найден')

            try:
                item = Link.objects.get(url=request.POST.get('link', ''), location__id=location_id)
            except Link.DoesNotExist:
                return HttpResponse(u'Ссылка не найдена')

            already_msg = u'Вы уже пожаловались на эту ссылку'

        else:
            return HttpResponse(u'Ошибка')

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
            Report.objects.create(item=item, reporter=request.user.get_profile(),
                    reason=reason, reason_explained=reason_explained)
        except IntegrityError:
            return HttpResponse()

        return HttpResponse('ok')

    return HttpResponse(u'Ошибка')
