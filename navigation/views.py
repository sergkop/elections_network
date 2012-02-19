# coding=utf8
import csv
import os.path
import re
import urllib

from HTMLParser import HTMLParser

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from locations.models import Location
from locations.utils import get_roles_counters, regions_list
from navigation.models import Page
from organizations.models import OrganizationCoverage
from users.models import Role

# create a subclass and override the handler methods
# TODO: reimplement usign scrapy
class CikHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.save_data = False
        self.data = ""

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and len(attrs) > 0 and attrs[0][1] == 'dotted':
            self.save_data = True

    def handle_endtag(self, tag):
        if self.save_data and tag == 'div':
            self.save_data = False

    def handle_data(self, data):
        if self.save_data:
            self.data += data

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

    # Если проводится запрос данных УИК, то сохранить их в специальный файл
    if request.GET.get('id') is None:
        data = urllib.urlopen(url_prefix+url, urllib.urlencode(request.GET)).read()
        
        parser = CikHTMLParser()
        parser.feed(data)
        
        if len(parser.data) > 0:
            fetch_uik_data = re.compile('№(\d+)[^:]+:\s(.+),\sтелефон:\s([^\r\n]+)')
            uik_data = fetch_uik_data.search(parser.data)

            save_uik_data(uik_data)
            
            if uik_data is not None and len(uik_data.groups()) == 3:
                data = "<p id=\"uik\">УИК №%s: %s, телефон %s</p>" % (uik_data.group(1),uik_data.group(2),uik_data.group(3))
                
        parser.close()
    # Если запрос части адреса
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

def save_uik_data(uik_data):
    if uik_data is None:
        return

    uiks_db_path = os.path.join(settings.PROJECT_PATH, 'media', 'address_cache', 'found_uiks_db.csv')
        
    if not os.path.exists(uiks_db_path):
        with open(uiks_db_path, 'w') as uiks_db_file:
            uiks_db_writer = csv.writer(uiks_db_file, delimiter=';', quotechar='"')
            uiks_db_writer.writerow(["№ УИК", "Адрес", "Телефон"])    

    with open(uiks_db_path, 'r') as uiks_db_file:
        uiks_db_reader = csv.reader(uiks_db_file, delimiter=';', quotechar='"')
        for uik in uiks_db_reader:
            if uik[0] == uik_data.group(1) and uik[1] == uik_data.group(2):
                return

    with open(uiks_db_path, 'a') as uiks_db_file:
        uiks_db_writer = csv.writer(uiks_db_file, delimiter=';', quotechar='"')
        uiks_db_writer.writerow([uik_data.group(1), uik_data.group(2), uik_data.group(3)])