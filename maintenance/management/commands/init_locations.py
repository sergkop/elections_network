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

def location_from_info(info):
    from locations.models import Location
    return Location(
        name = info['name'],

        postcode = info['postcode'],
        address = info['address'],
        telephone = info.get('telephone', ''),
        email = info.get('email', ''),

        x_coord = info.get('x_coord'),
        y_coord = info.get('y_coord'),

        vrnorg = int(info['vrnorg']) if 'vrnorg' in info else None,
        vrnkomis = int(info['vrnkomis']) if 'vrnkomis' in info else None,
        tvd = int(info.get('tvd', 0)),
        root = int(info.get('root', 0)),
    )

class Command(BaseCommand):
    help = "Loads locations data after first syncdb."

    def handle(self, *args, **options):
        REGIONS = {}
        region_ids_path = os.path.join(settings.PROJECT_PATH, 'data', 'region_ids.txt')
        for line in open(region_ids_path):
            region_title, region_name, region_id = line.split(', ')
            REGIONS[region_name] = (region_title, int(region_id.strip()))

        i = 0
        for region in REGIONS:
            print_progress(i, len(REGIONS))

            # Init regional comission
            info = json.loads(open(data_path(region, 'center')).read().decode('utf8'))
            regional_location = location_from_info(info)
            regional_location.name = REGIONS[region][0]
            regional_location.region_name = region
            regional_location.region_code = REGIONS[region][1]
            regional_location.save()

            # Init TIKs
            info_list = json.loads(open(data_path(region, 'merge')).read().decode('utf8'))
            for info in info_list:
                tik = location_from_info(info)
                tik.region = regional_location
                tik.region_name = region
                tik.region_code = REGIONS[region][1]
                tik.save()

            i += 1
