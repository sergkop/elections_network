from django.db import IntegrityError
from django.http import HttpResponse

from links.models import Link, ReportLink

def add_link(request):
    if request.method=='POST' and request.user.is_authenticated():
        try:
            location_id = int(request.POST.get('location', ''))
        except ValueError:
            return HttpResponse('fail1')

        try:
            link = Link.objects.create(location_id=location_id, user=request.user,
                    url=request.POST.get('url', ''), name=request.POST.get('name', ''))
        except IntegrityError:
            return HttpResponse('fail2')

        return HttpResponse('ok')

    return HttpResponse('fail3')

def report_link(request):
    if request.method=='POST' and request.user.is_authenticated():
        try:
            location_id = int(request.POST.get('location', ''))
        except ValueError:
            return HttpResponse('fail1')

        try:
            link = Link.objects.get(url=request.POST.get('report_link_radio', ''), location__id=location_id)
        except Link.DoesNotExist:
            return HttpResponse('fail2')

        try:
            ReportLink.objects.create(link=link, user=request.user)
        except IntegrityError:
            return HttpResponse('fail3')

        return HttpResponse('ok')

    return HttpResponse('fail4')
