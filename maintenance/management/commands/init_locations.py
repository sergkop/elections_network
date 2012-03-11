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
    help = "Loads locations data after first syncdb."

    def handle(self, *args, **options):
        REGIONS = {}
        region_ids_path = os.path.join(settings.PROJECT_PATH, 'data', 'region_ids.txt')
        for line in open(region_ids_path):
            region_title, region_name, region_id = line.split(', ')
            REGIONS[region_name] = (region_title, int(region_id.strip()))

        """
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

        # Init foreign countries
        from locations.models import FOREIGN_CODE, FOREIGN_NAME, FOREIGN_TERRITORIES
        foreign = location_from_info({'name': FOREIGN_TERRITORIES, 'postcode': 0, 'address': ''})
        foreign.region_name = FOREIGN_NAME
        foreign.region_code = FOREIGN_CODE
        foreign.save()

        countries_path = os.path.join(settings.PROJECT_PATH, 'data', 'countries.txt')
        for country in open(countries_path):
            location = location_from_info({'name': country.strip(), 'postcode': 0, 'address': ''})
            location.region_name = FOREIGN_NAME
            location.region_code = FOREIGN_CODE
            location.region = foreign
            location.save()
        """

        # init uiks
        from locations.models import Location
        for region in REGIONS:
            print region

            region_location = Location.objects.get(region_name=region, region=None)

            uiks_path = os.path.join(settings.PROJECT_PATH, 'data', 'regions', region+'.json')
            tiks_list = json.loads(open(uiks_path).read().decode('utf8'))
            j = 0
            for tik in tiks_list:
                try:
                    tik_location = Location.objects.get(region=region_location, tvd=tik['tvd'])
                except Location.DoesNotExist:
                    print region, tik['tvd']
                    continue

                print_progress(j, len(tiks_list))
                for uik_data in tik['sub']:
                    if uik_data['name'].startswith(u'УИК №'):
                        uik_data['name'] = uik_data['name'][5:]
                    else:
                        print uik_data['name'], region
                        raise ValueError

                    uik = location_from_info(uik_data)

                    uik.region = region_location
                    uik.tik = tik_location

                    uik.region_name = region
                    uik.region_code = REGIONS[region][1]

                    uik.save()

                j += 1
