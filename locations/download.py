# coding=utf8
import cookielib
import json
import os.path
from random import choice
import re
import urllib2

from scrapy.selector import HtmlXPathSelector

region_name_re = re.compile(r'(\d{1,4}\s)?(.*)')
def strip_prefix_number(name):
    m = region_name_re.match(name)
    return m.group(2)

# for gos duma elections
#START_URL = 'http://www.vybory.izbirkom.ru/region/izbirkom?action=show&root_a=1000087&vrn=100100028713299&region=0&global=true&type=0&sub_region=0&prver=0&pronetvd=null'

# for president elections
#START_URL = 'http://www.vybory.izbirkom.ru/region/izbirkom?action=show&global=1&vrn=100100031793505&region=0&prver=0&pronetvd=null'

#REGIONS_LIST_URL = 'http://www.cikrf.ru/sites/'

RESULTS_ROOT_URL = 'http://www.%(name)s.vybory.izbirkom.ru/region/%(name)s?action=show&global=1&vrn=100100031793505&region=%(region_id)s&prver=0&pronetvd=null'
INFO_ROOT_URL = 'http://www.%(name)s.vybory.izbirkom.ru/region/%(name)s?action=show_komissia&region=%(region_id)s&sub_region=%(region_id)s&type=100&vrnorg=0&vrnkomis=0'

USER_AGENTS = [
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.5) Gecko/20091114 Gentoo Firefox/3.5.5',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.0',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729)',
    'Opera/9.62 (Windows NT 6.0; U; en) Presto/2.1.1',
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3',
]

def read_url(url):
    print url
    proxy_handler = urllib2.ProxyHandler()
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(proxy_handler, urllib2.HTTPCookieProcessor(cj))
    request = urllib2.Request(url, headers={'User-Agent': choice(USER_AGENTS)})
    try:
        return opener.open(request).read().decode('windows-1251')
    except urllib2.URLError, e:
        raise e
        return ''

def get_subregions(url, selector):
    """ Get {name: url} dict with subregions data """
    regions = {}
    for option in HtmlXPathSelector(text=read_url(url)).select(selector):
        value = option.select("@value").extract()
        name = option.select("text()").extract()[0].strip()
        if value:
            regions[name] = value[0]

    return regions

def build_structure(url, lst):
    for name, sub_url in get_subregions(url, "//select[@name='gs']//option").iteritems():
        location = {'name': strip_prefix_number(name), 'sub': []}
        for param in sub_url.split('?')[1].split('&'):
            param_name, param_value = param.split('=')
            if param_name in ('root', 'tvd'):
                location[param_name] = param_value
        lst.append(location)

        if u'УИК' not in name:
            build_structure(sub_url, location['sub'])

def download_structure():
    data_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data')
    f = open(os.path.join(data_path, 'region_ids.txt'))
    for line in f:
        title, name, region_id = line.split(', ')
        region_id = region_id.strip()

        # get struct data
        struct_path = os.path.join(data_path, 'regions', name+'.json')
        if not os.path.exists(struct_path):
            url = RESULTS_ROOT_URL % {'name': name, 'region_id': region_id}
            struct = []
            build_structure(url, struct)
            
            with open(struct_path, 'w') as region_file:
                region_file.write(json.dumps(struct, indent=4, ensure_ascii=False).encode('utf8'))

        info_path = os.path.join(data_path, 'regions', name+'-info.json')
        if not os.path.exists(info_path):
            url = INFO_ROOT_URL % {'name': name, 'region_id': region_id}
            info = []

            for link in HtmlXPathSelector(text=read_url(url)).select("//td[@width='40%' and @valign='top']//a"):
                sub_url = link.select("@href").extract()[0]

                # remove standard prefixes
                comission_name = link.select("text()").extract()[0].strip()
                for phrase in (u'территориальная избирательная комиссия',
                        u'избирательная комиссия', u'муниципального образования'):
                    index = comission_name.lower().find(phrase)
                    if index != -1:
                        comission_name = comission_name[:index] + comission_name[index+len(phrase)+1:]

                data = {'name': comission_name}

                for param in sub_url.split('?')[1].split('&'):
                    param_name, param_value = param.split('=')
                    if param_name in ('vrnorg', 'vrnkomis'):
                        data[param_name] = param_value

                hxs = HtmlXPathSelector(text=read_url(sub_url))
                values = hxs.select("//td[@width='60%' and @valign='top']//tr[1]//table[@vspace='0']//tr[2]/td/text()").extract()
                data['address'] = values[0]
                if len(values) > 2:
                    if '@' in values[-2]:
                        data['email'] = values[-2].strip()
                    if '@' not in values[1]:
                        data['telephone'] = values[1].replace(u'\u00a0', ' ')

                info.append(data)

            with open(info_path, 'w') as info_file:
                info_file.write(json.dumps(info, indent=4, ensure_ascii=False).encode('windows-1251'))

if __name__ == '__main__':
    download_structure()
