from django.http import HttpResponse

from links.models import LinkModel

def add_link(request):
    print request.is_ajax(), request.method=='POST', request.user.is_authenticated()
    if request.method=='POST' and request.user.is_authenticated():
        link = LinkModel.objects.create(
                location_id=int(request.POST.get('location', '')),
                user=request.user,
                url=request.POST.get('url', ''),
                name=request.POST.get('name', '')
        )
        return HttpResponse('ok')

    return HttpResponse('fail')
