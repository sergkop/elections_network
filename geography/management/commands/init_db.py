import json
import os.path

from django.conf import settings
from django.core.management.base import BaseCommand

def iterate_struct(data, seq):
    for sub_region, sub_data in data['sub'].iteritems():
        yield seq + [sub_region]
        for loc in iterate_struct(sub_data, seq+[sub_region]):
            yield loc

class Command(BaseCommand):
    help = "Loads geography data after first syncdb."

    def handle(self, *args, **options):
        from geography.models import LocationModel

        db_entries = {}

        # TODO: remove numbers in the beginning of the name
        data = json.loads(open(os.path.join(settings.PROJECT_PATH, 'regions.json')).read())
        for location in iterate_struct(data, []):
            if len(location) == 1:
                db_entries[location[0]] = {'entry': LocationModel.objects.create(name=location[0]), 'sub': {}}
            elif len(location) == 2:
                db_entries[location[0]]['sub'][location[1]] = \
                        LocationModel.objects.create(name=location[1], parent_1=db_entries[location[0]]['entry'])
            elif len(location) == 3:
                LocationModel.objects.create(name=location[2], parent_1=db_entries[location[0]]['entry'],
                        parent_2=db_entries[location[0]]['sub'][location[1]])

        print LocationModel.objects.count()
