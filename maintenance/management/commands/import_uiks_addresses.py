import re

from django.core.management.base import BaseCommand

re_data_line = re.compile(r'^(\d+);"(.*)";"SRID=4326;POINT\(([\d.]+) ([\d.]+)\)";(\d+)$')

class Command(BaseCommand):
    help = "Import uiks addresses."

    def handle(self, *args, **options):
        from locations.models import Location
        print len(open(args[0], 'r').readlines())
        i = 0
        for line in open(args[0], 'r'):
            i += 1
            print i
            line = line.strip()
            m = re_data_line.search(line)
            if m:
                uik = int(m.group(1))
                address = m.group(2)
                x_coord = float(m.group(3))
                y_coord = float(m.group(4))
                region_code = int(m.group(5))

                address = address.decode('utf8')
                if len(address) >= 200:
                    print line
                    continue

                try:
                    location = Location.objects.exclude(tik=None).get(name=uik, region_code=region_code)
                except Location.DoesNotExist:
                    print line
                    continue
                else:
                    location.address = address
                    location.x_coord = x_coord
                    location.y_coord = y_coord
                    location.save()
            else:
                print line
                continue
