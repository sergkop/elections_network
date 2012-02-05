import json
import os.path
#import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand

#region_name_re = re.compile(r'(\d{1,3}\s)?(.*)')
#def strip_prefix_number(name):
#    m = region_name_re.match(name)
#    return m.group(2)

def iterate_struct(data, seq):
    for sub_region, sub_data in data['sub'].iteritems():
        #sub_region = strip_prefix_number(sub_region)
        yield seq + [sub_region]
        for loc in iterate_struct(sub_data, seq+[sub_region]):
            yield loc

def print_progress(i, count):
    """ Show progress message updating in-place """
    if i < count-1:
        sys.stdout.write("\r%(percent)2.1f%%" % {'percent': 100*float(i)/count})
        sys.stdout.flush()
    else:
        sys.stdout.write("\r")
        sys.stdout.flush()

default_location_fields = {'postcode': 0, 'tvd': 0, 'root': 0, 'vrnorg': 0, 'vrnkomis': 0,
        'x_coord': 0, 'y_coord': 0}

class Command(BaseCommand):
    help = "Loads locations data after first syncdb."

    def handle(self, *args, **options):
        from locations.models import Location
        from navigation.models import Page

        db_entries = {}

        print "initializing static pages"
        pages_data = open(os.path.join(settings.PROJECT_PATH, 'data', 'pages_data.json')).read()
        data = json.loads(pages_data)
        for name, html in data.iteritems():
            Page.objects.create(name=name, content=html)

        print "loading the regions hierarchy"
        data = json.loads(open(os.path.join(settings.PROJECT_PATH, 'data', 'regions-gosduma.json')).read())
        i = 0
        for location in iterate_struct(data, []):
            print_progress(i, 100)
            if len(location) == 1:
                db_entries[location[0]] = {'entry': Location.objects.create(name=location[0], **default_location_fields), 'sub': {}}
            elif len(location) == 2:
                db_entries[location[0]]['sub'][location[1]] = \
                        Location.objects.create(name=location[1], parent_1=db_entries[location[0]]['entry'], **default_location_fields)
            elif len(location) == 3:
                Location.objects.create(name=location[2], parent_1=db_entries[location[0]]['entry'],
                        parent_2=db_entries[location[0]]['sub'][location[1]], **default_location_fields)
            i += 1
            
            if i > 100:
                break # artificial break to speed up data loading

