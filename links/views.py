from django.db import IntegrityError
from django.http import HttpResponse

from links.models import LinkModel, ReportLinkModel

def add_link(request):
    if request.method=='POST' and request.user.is_authenticated():
        try:
            link = LinkModel.objects.create(
                    location_id=int(request.POST.get('location', '')),
                    user=request.user,
                    url=request.POST.get('url', ''),
                    name=request.POST.get('name', '')
            )
        except IntegrityError:
            return HttpResponse('fail')
        return HttpResponse('ok')

    return HttpResponse('fail')

def report_link(request):
    if request.method=='POST' and request.user.is_authenticated():
        link = LinkModel.objects.get(url=request.POST.get('report_link_radio', ''),
                    location__id=int(request.POST.get('location', '')))
        try:
            link = LinkModel.objects.get(url=request.POST.get('report_link_radio', ''),
                    location__id=int(request.POST.get('location', '')))
        except: # TODO: write exception
            return HttpResponse('fail')

        try:
            ReportLinkModel.objects.create(link=link, user=request.user)
        except IntegrityError:
            return HttpResponse('fail')

        return HttpResponse('ok')

    return HttpResponse('fail')
