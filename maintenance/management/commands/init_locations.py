import json
import os.path
import sys

from django.conf import settings
from django.core.management.base import BaseCommand

def print_progress(i, count):
    """ Show progress message updating in-place """
    if i < count-1:
        sys.stdout.write("\r%(percent)2.1f%%" % {'percent': 100*float(i)/count})
        sys.stdout.flush()
    else:
        sys.stdout.write("\r")
        sys.stdout.flush()

def data_path(region, type):
    return os.path.join(settings.PROJECT_PATH, 'data', 'regions', '%s-%s.json' % (region, type))

class Command(BaseCommand):
    help = "Loads locations data after first syncdb."

    def handle(self, *args, **options):
        region_ids = json.loads(open().read())

        REGIONS = {}
        region_ids_path = os.path.join(settings.PROJECT_PATH, 'data', 'region_ids.json')
        for line in open(regions_ids_path):
            region_title, region_name, region_id = line.split(', ')
            REGIONS[region_name] = region_title

        i = 0
        for region in REGIONS:
            print_progress(i, len(REGIONS))

            # TODO: temporary check
            if os.path.exists(data_path(region, 'merge')) and os.path.exists(data_path(region, 'center')):
                info = json.loads(open(data_path(region, 'center')).read().decode('utf8'))

                Location(
                    name = info['name'],

                    postcode = info['postcode'],
                    address = info['address'],
                    telephone = info.get('telephone', ''),
                    email = info.get('email', ''),

                    x_coord = info.get('x_coord'),
                    y_coord = info.get('y_coord'),

                    vrnorg = int(info['vrnorg']),
                    vrnkomis = int(info['vrnkomis']),
                    tvd = int(info.get('tvd', 0)),
                    root = int(info.get('root', 0)),
                ).save()

            i += 1
