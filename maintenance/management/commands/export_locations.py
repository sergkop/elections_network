import json

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Export locations data. First parameter is the full path to results file."

    def handle(self, *args, **options):
        from locations.models import Location

        location_data = []
        for location in Location.objects.all():
            if location.tik_id:
                parent_id = location.tik_id
            elif location.region_id:
                parent_id = location.region_id
            else:
                parent_id = None

            if location.is_region():
                level = 'region'
            elif location.is_tik():
                level = 'tik'
            elif location.is_uik():
                level = 'uik'

            location_data.append({
                'id': location.id,
                'name': location.name,
                'postcode': location.postcode,
                'address': location.address,
                'telephone': location.telephone,
                'email': location.email,
                'parent_id': parent_id,
                'x_coord': location.x_coord,
                'y_coord': location.y_coord,
                'level': level,
            })

        with open(args[0], 'w') as f:
            f.write(json.dumps(location_data, indent=4, ensure_ascii=False).encode('utf8'))
