import cookielib
from random import choice
import sys
import urllib2

from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from scrapy.selector import HtmlXPathSelector

USER_AGENTS = [
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.5) Gecko/20091114 Gentoo Firefox/3.5.5',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.0',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729)',
    'Opera/9.62 (Windows NT 6.0; U; en) Presto/2.1.1',
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3',
]

def print_progress(i, count):
    """ Show progress message updating in-place """
    if i < count-1:
        sys.stdout.write("\r%(percent)2.3f%%" % {'percent': 100*float(i)/count})
        sys.stdout.flush()
    else:
        sys.stdout.write("\r")
        sys.stdout.flush()

def read_url(url):
    #print url
    proxy_handler = urllib2.ProxyHandler()
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(proxy_handler, urllib2.HTTPCookieProcessor(cj))
    request = urllib2.Request(url, headers={'User-Agent': choice(USER_AGENTS)})
    try:
        return opener.open(request).read().decode('windows-1251')
    except urllib2.URLError, e:
        raise e
        return ''

class Command(BaseCommand):
    help = "Import election results from cikrf.ru"

    def handle(self, *args, **options):
        from locations.models import Location
        from organizations.models import Organization
        from protocols.models import Protocol

        organization = Organization.objects.get(name='cik')
        content_type = ContentType.objects.get_for_model(Organization)

        locations_processed = Protocol.objects.filter(content_type=content_type, object_id=organization.id) \
                .values_list('location', flat=True)
        uiks_count = Location.objects.exclude(tik=None).count()
        j = len(locations_processed)
        for location in Location.objects.exclude(tik=None).exclude(id__in=locations_processed):
            trs = HtmlXPathSelector(text=read_url(location.results_url())) \
                    .select("//table[@width='100%' and @cellspacing='1' and @cellpadding='2' and @bgcolor='#ffffff']//tr")
            #trs = list(HtmlXPathSelector(text=read_url(location.results_url())) \
            #        .select("//body//table[3]//tr[4]//td//table[6]//tr"))

            del trs[18]
            assert len(trs) == 23, "incorrect number of rows"

            data = {}
            for i in range(23):
                data['p'+str(i+1)] = int(trs[i].select(".//b/text()").extract()[0])

            data.update({'location': location, 'verified': True})

            Protocol.objects.get_or_create(content_type=content_type, object_id=organization.id,
                    protocol_id=location.id, defaults=data)

            print_progress(j, uiks_count)
            j += 1
