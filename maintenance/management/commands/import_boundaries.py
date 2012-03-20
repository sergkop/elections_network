import json
import os.path

from django.conf import settings
from django.core.management.base import BaseCommand

from grakon.utils import print_progress

class Command(BaseCommand):
    help = "Import region boundaries"

    def handle(self, *args, **options):
        from locations.models import Boundary

        for i in range(1, 90):
            data = json.loads(open(os.path.join(
                    settings.PROJECT_PATH, 'grakon', 'static', 'districts', str(i)+'s.json')).read())

            for feature in data['features']:
                properties = feature['properties']
                geometry = feature['geometry']['coordinates'][0][0]

                data_to_save = {'properties': properties, 'geometry': geometry}
                Boundary(data=json.dumps(data_to_save),
                        x_min=min(point[0] for point in geometry),
                        x_max=max(point[0] for point in geometry),
                        y_min=min(point[1] for point in geometry),
                        y_max=max(point[1] for point in geometry)
                ).save()

            print_progress(i, 90)
