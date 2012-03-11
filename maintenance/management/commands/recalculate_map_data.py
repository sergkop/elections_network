from collections import Counter
import json

from django.core.management.base import BaseCommand

from grakon.utils import print_progress

class Command(BaseCommand):
    help = "Recalculate map data"

    def handle(self, *args, **options):
        from locations.models import Location
        from loginza.models import UserMap
        from protocols.models import Protocol
        from users.models import Role

        locations = list(Location.objects.values_list('id', 'region', 'tik'))

        locations_by_id = {}
        for loc_id, region_id, tik_id in locations:
            locations_by_id[loc_id] = (region_id, tik_id)

        inactive_ids = UserMap.objects.filter(verified=False).values_list('user', flat=True)
        roles = list(Role.objects.exclude(user__user__email='', user__user__is_active=False,
                user__in=inactive_ids).values_list('location', 'type'))

        # Calculate roles distribution
        roles_by_location = {}
        for loc_id, role_type in roles:
            roles_by_location.setdefault(loc_id, []).append(role_type)

        data_by_location = {}
        for loc_id in locations_by_id:
            data_by_location[loc_id] = Counter(roles_by_location.get(loc_id, []))

        # Add uiks counts to tiks
        for loc_id in locations_by_id:
            region_id, tik_id = locations_by_id[loc_id]
            if tik_id: # only process uiks
                data_by_location[tik_id] += data_by_location[loc_id]

        # Add tiks counts to regions
        for loc_id in locations_by_id:
            region_id, tik_id = locations_by_id[loc_id]
            if region_id and tik_id is None: # only process tiks
                data_by_location[region_id] += data_by_location[loc_id]

        # Add cik data
        protocols_by_location = {}
        for protocol in Protocol.objects.from_cik():
            protocols_by_location[protocol.location_id] = protocol

        for loc_id in protocols_by_location:
            pr = protocols_by_location[loc_id]
            data_by_location[loc_id].update(p9=pr.p9, p19=pr.p19, p20=pr.p20, p21=pr.p21,
                    p22=pr.p22, p23=pr.p23)

        # Recalculate uiks
        i = 0
        count = Location.objects.count()
        for location in Location.objects.all():
            prev_value = location.data
            location.data = json.dumps(data_by_location[location.id])
            if location.data != prev_value:
                location.save()

            i += 1
            print_progress(i, count)
