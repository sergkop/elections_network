# coding=utf8
import os.path
import re
import urllib

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from locations.models import Location
from locations.utils import get_roles_counters, regions_list
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
        'name': 'main',
        'counters': get_roles_counters(None),
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
        'name': 'map',
        'place': request.GET.get('place', ''),
    }
    return render_to_response('map.html', context_instance=RequestContext(request, context))

def uik_search(request):
    return render_to_response('uik_search.html', context_instance=RequestContext(request))

def uik_search_data(request):
    url = request.GET.get('url')

    if not url:
        return HttpResponse(u'Необходимо указать url')

    url_prefix = 'http://cikrf.ru/dynservices/gas/serviceone/'

    if request.GET.get('id') is None:
        data = urllib.urlopen(url_prefix+url, urllib.urlencode(request.GET)).read()
    else:
        cache_path = os.path.join(settings.PROJECT_PATH, 'media', 'address_cache',
                cache_file_name( request.GET.get('id') ))

        if not os.path.exists(cache_path):
            data = urllib.urlopen(url_prefix+url, urllib.urlencode(request.GET)).read()
            with open(cache_path, 'w') as cache_file:
                cache_file.write(data)

        with open(cache_path, 'r') as cache_file:
            data = cache_file.read()
    return HttpResponse(data)

def cache_file_name(id):
    file_parts = re.findall(r'\w+',id)
    file_name = "".join(file_parts)

    if file_name == "":
        return "wrong_id.json"

    return file_name + ".json"
