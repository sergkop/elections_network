#!/usr/bin/python
# -*- coding: UTF-8 -*-

import urllib2, re,json

url = 'http://www.vybory.izbirkom.ru/region/region/izbirkom?action=show&root=1&tvd=100100028713304&vrn=100100028713299&region=0&global=1&sub_region=0&prver=0&pronetvd=null&vibid=100100028713304&type=233'

def get_names(html):
    pattern = u'(?<=TEXT-DECORATION: none" href=")\S+">[а-яА-ЯёЁ \-()]+'
    names = []
    strings = re.findall(pattern,html)
    for string in strings:
        url, name = string.split('">')
        names.append({'name':name,'url':url})
    return names

response = urllib2.urlopen(url)
html = response.read()
html = html.decode('cp1251')

def without_url(dict):
    result = copy(dict)
    if 'url' in result:
        result.pop('url')
    return result

regions = get_names(html)
regions_2 = [without_url(region) for region in regions]

for x in xrange(len(regions)):
    region = regions[x]
    url = region['url']
    response = urllib2.urlopen(url)
    html = response.read()
    html = html.decode('cp1251')
    sub_regions = get_names(html)
    region.update({'sub-regions':sub_regions})
    regions_2[x].update({'sub-regions':[without_url(sub_region) for sub_region in sub_regions]})
    print json.dumps(region, sort_keys=True, indent=4)

f = open('C:/desk/regions.txt','w')
f.write(json.dumps(regions_2, sort_keys=True, indent=4))
f.close()