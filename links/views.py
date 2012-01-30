# coding=utf8
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.http import HttpResponse

from links.models import Link

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
