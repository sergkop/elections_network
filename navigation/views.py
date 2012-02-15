# coding=utf8
import urllib
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.utils import simplejson as json

from locations.models import Location
from locations.utils import regions_list
from navigation.models import Page
from organizations.models import OrganizationCoverage
from users.models import Role

def main(request):
    voter_count = Role.objects.filter(type='voter').count()
    """
    if voter_count%10 == 1:
        ending = u'ь'
    elif voter_count%10 in (2, 3, 4):
        ending = u'я'
    else:
        ending = u'ей'
    """

    sub_regions = regions_list()
    context = {
        'voter_count': voter_count,
        #'ending': ending,
        'locations': sub_regions,
        'sub_regions': sub_regions,
        'organizations': OrganizationCoverage.objects.organizations_at_location(None),
    }
    return render_to_response('main.html', context_instance=RequestContext(request, context))

def static_page(request, name, template):
    #page = get_object_or_404(Page, name=name)
    context = {
        #'content': page.content,
        'tab': name,
        'template': template,
    }
    return render_to_response(template, context_instance=RequestContext(request, context))

def map_search(request):
    context = {
        'place': request.GET.get('place', ''),
    }
    return render_to_response('map.html', context_instance=RequestContext(request, context))

def uik_search(request):
	url = request.REQUEST.get('url', None)
	if url is not None:
		response = urllib.urlopen(request.REQUEST.get('url'), urllib.urlencode(request.REQUEST)).read()
		return HttpResponse(response)
	else:
		return render_to_response('uik_search.html', context_instance=RequestContext(request))
