# -*- coding:utf-8 -*-
import csv
from HTMLParser import HTMLParser
import os.path
import re
import urllib

from django.conf import settings

re_uik_data = re.compile('№(\d+)[^:]+:\s(.+),\sтелефон:\s([^\r\n]+)')

# create a subclass and override the handler methods
# TODO: reimplement usign scrapy or beautifulsoap
class CikHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.save_data = False
        self.data = ""

    def handle_starttag(self, tag, attrs):
        if tag=='div' and len(attrs)>0 and attrs[0][1]=='dotted':
            self.save_data = True

    def handle_endtag(self, tag):
        if self.save_data and tag=='div':
            self.save_data = False

    def handle_data(self, data):
        if self.save_data:
            self.data += data

def get_uik_data(get_data):
    res = ''
    url_prefix = 'http://cikrf.ru/dynservices/gas/serviceone/'

    url = get_data.get('url')
    if not url:
        return u'Необходимо указать url'

    # Если проводится запрос данных УИК, то сохранить их в специальный файл
    if get_data.get('id') is None:
        data = urllib.urlopen(url_prefix+url, urllib.urlencode(get_data)).read()

        parser = CikHTMLParser()
        parser.feed(data)

        if len(parser.data) > 0:
            # TODO: what if telephone is missing in the address
            uik_data = re_uik_data.search(parser.data)

            if uik_data:
                save_uik_data(uik_data)

                if len(uik_data.groups()) == 3:
                    # TODO: eliminate html here
                    res = '<p id="uik">УИК №%s: %s, телефон %s</p>' % (
                            uik_data.group(1), uik_data.group(2), uik_data.group(3))

        parser.close()
    else:
        # Если запрос части адреса
        # TODO: caching is not effective for two servers
        # TODO: too many files in one folder is bad
        cache_path = os.path.join(settings.PROJECT_PATH, 'media', 'address_cache',
                cache_file_name(get_data.get('id')))

        if not os.path.exists(cache_path):
            res = urllib.urlopen(url_prefix+url, urllib.urlencode(get_data)).read()
            with open(cache_path, 'w') as cache_file:
                cache_file.write(res)
        else:
            with open(cache_path, 'r') as cache_file:
                res = cache_file.read()

    return res

def cache_file_name(id):
    # TODO: what is it for?
    file_parts = re.findall(r'\w+', id)
    file_name = ''.join(file_parts)

    if file_name == '':
        return 'wrong_id.json'

    return file_name+'.json'

# TODO: do we need this cvs file? + it is not scalable
def save_uik_data(uik_data):
    uiks_db_path = os.path.join(settings.PROJECT_PATH, 'media', 'address_cache', 'found_uiks_db.csv')

    if not os.path.exists(uiks_db_path):
        with open(uiks_db_path, 'w') as uiks_db_file:
            uiks_db_writer = csv.writer(uiks_db_file, delimiter=';', quotechar='"')
            uiks_db_writer.writerow(['№ УИК', 'Адрес', 'Телефон'])

    with open(uiks_db_path, 'r') as uiks_db_file:
        uiks_db_reader = csv.reader(uiks_db_file, delimiter=';', quotechar='"')
        for uik in uiks_db_reader:
            if uik[0]==uik_data.group(1) and uik[1]==uik_data.group(2):
                return

    with open(uiks_db_path, 'a') as uiks_db_file:
        uiks_db_writer = csv.writer(uiks_db_file, delimiter=';', quotechar='"')
        uiks_db_writer.writerow([uik_data.group(1), uik_data.group(2), uik_data.group(3)])
