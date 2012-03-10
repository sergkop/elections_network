# -*- coding:utf-8 -*-
import json
import os.path

from django.conf import settings
from django.core.management.base import BaseCommand

from grakon.utils import print_progress

def data_path(region, type):
    return os.path.join(settings.PROJECT_PATH, 'data', 'regions', '%s-%s.json' % (region, type))

def location_from_info(info):
    from locations.models import Location
    return Location(
        name = info['name'],

        postcode = info.get('postcode'),
        address = info.get('address', ''),
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
    help = "Update locations data with new CIK data."

    def handle(self, *args, **options):
        from locations.models import Location
        REGIONS = {}
        region_ids_path = os.path.join(settings.PROJECT_PATH, 'data', 'region_ids.txt')
        for line in open(region_ids_path):
            region_title, region_name, region_id = line.split(', ')
            REGIONS[region_name] = (region_title, int(region_id.strip()))

        i = 0
        for region in REGIONS:
            print_progress(i, len(REGIONS))

            region_location = Location.objects.get(region=None, region_name=region)

            # Update TIKs
            info_list = json.loads(open(os.path.join(settings.PROJECT_PATH, 'data', 'regions', '%s.json' % region)).read().decode('utf8'))
            for tik_info in info_list:
                try:
                    tik = Location.objects.filter(region_name=region, tik=None).get(tvd=tik_info['tvd'])
                except Location.DoesNotExist:
                    tik = location_from_info(tik_info)
                    tik.region = region_location
                    tik.region_name = region
                    tik.region_code = REGIONS[region][1]
                    tik.save()
                    print "new tik", tik.id

                uiks_by_number = {}
                for uik in list(Location.objects.filter(tik=tik)):
                    uiks_by_number[uik.name] = uik

                for uik_data in tik_info['sub']:
                    if uik_data['name'].startswith(u'УИК №'):
                        uik_data['name'] = uik_data['name'][5:]
                    else:
                        print uik_data['name'], region
                        raise ValueError

                    if uik_data['name'] in uiks_by_number:
                        uik = uiks_by_number[uik_data['name']]
                        if uik.tvd!=int(uik_data['tvd']) or uik.root!=int(uik_data['root']):
                            #print "update uik", region, uik.tvd, uik_data['tvd'], uik_data['name']
                            uik.tvd = uik_data['tvd']
                            uik.root = uik_data['root']
                            uik.save()
                    else:
                        #print "new uik", region, uik_data['name']
                        uik = location_from_info(uik_data)

                        uik.region = region_location
                        uik.tik = tik

                        uik.region_name = region
                        uik.region_code = REGIONS[region][1]

                        uik.save()

                # Remove UIKs
                number_list = [uik_data['name'] for uik_data in tik_info['sub']]
                for old_tik in list(Location.objects.filter(tik=tik).exclude(name__in=number_list)):
                    print "UIK to delete", old_tik.id

            i += 1
