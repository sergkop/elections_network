# coding=utf8
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from locations.models import Location
from navigation.models import Page
from users.models import Role

def main(request):
    voter_count = Role.objects.filter(type='voter').count()
    if voter_count%10 == 1:
        ending = u'ь'
    elif voter_count%10 in (2, 3, 4):
        ending = u'я'
    else:
        ending = u'ей'

    context = {
        'voter_count': voter_count,
        'ending': ending,
        'locations': list(Location.objects.filter(parent_1=None).order_by('name')),
    }
    return render_to_response('main.html', context_instance=RequestContext(request, context))

def static_page(request, name, template):
    page = get_object_or_404(Page, name=name)
    context = {
        'content': page.content,
    }
    return render_to_response(template, context_instance=RequestContext(request, context))
