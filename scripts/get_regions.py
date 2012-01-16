import cookielib
import json
import os.path
from random import choice
import urllib2

from scrapy.selector import HtmlXPathSelector

START_URL = "http://www.vybory.izbirkom.ru/region/izbirkom?action=show&root_a=1000087&vrn=100100028713299&region=0&global=true&type=0&sub_region=0&prver=0&pronetvd=null"

USER_AGENTS = [
    "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.5) Gecko/20091114 Gentoo Firefox/3.5.5",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.0",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729)",
    "Opera/9.62 (Windows NT 6.0; U; en) Presto/2.1.1"
    "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3",
]

def read_url(url):
    print url
    proxy_handler = urllib2.ProxyHandler()
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(proxy_handler, urllib2.HTTPCookieProcessor(cj))
    request = urllib2.Request(url, headers={'User-Agent': choice(USER_AGENTS)})
    try:
        return opener.open(request).read()
    except urllib2.URLError, e:
        raise e
        return ''

def parse_region_page(url):
    regions = {}
    hxs = HtmlXPathSelector(text=read_url(url).decode('windows-1251'))

    for option in hxs.select("//select[@name='gs']//option"):
        value = option.select("@value").extract()
        name = option.select("text()").extract()[0].strip()
        if value:
            regions[name] = value[0]

    return regions

def build_structure(struct):
    for region, url in parse_region_page(struct['url']).iteritems():
        struct['sub'][region] = {'url': url, 'sub': {}}
        build_structure(struct['sub'][region])

if __name__ == '__main__':
    structure = {'url': START_URL, 'sub': {}}
    build_structure(structure)

    data_path = os.path.join(os.path.dirname(__file__), 'regions.json') 
    with open(data_path, 'w') as f:
        f.write(json.dumps(structure, indent=4))
