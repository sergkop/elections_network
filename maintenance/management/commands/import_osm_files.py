import os

from django.conf import settings
from django.core.management.base import BaseCommand

from lxml.etree import fromstring

from grakon.utils import print_progress

class Command(BaseCommand):
    help = "Import exact uik locations from osm files"

    def handle(self, *args, **options):
        from locations.models import Location

        skip = 0
        osm_dir_path = os.path.join(settings.PROJECT_PATH, 'data', 'osm')
        files = [data[2] for data in os.walk(osm_dir_path)][0]
        for filename in files:
            xml = fromstring(open(os.path.join(osm_dir_path, filename)).read())

            i = 0
            for node in xml:
                if node.tag != 'node':
                    continue

                attrs = dict((tag.get('k'), tag.get('v')) for tag in node)

                if not (('addr:city' in attrs) and ('addr:street' in attrs) and \
                        ('addr:housenumber' in attrs) and ('ref' in attrs)):
                    skip += 1
                    continue

                try:
                    location = Location.objects.get(region_name=filename[:-4], name=attrs['ref'])
                except Location.DoesNotExist:
                    skip += 1
                    continue
                else:
                    location.x_coord = float(node.get('lon'))
                    location.y_coord = float(node.get('lat'))

                    location.address = '%s, %s %s' % (attrs['addr:city'],
                            attrs['addr:street'], attrs['addr:housenumber'])

                    if attrs.get('phone', ''):
                        location.telephone = attrs.get('phone', '')

                    location.save()

                print_progress(i, len(xml))
                i += 1

        print "skipped", skip
