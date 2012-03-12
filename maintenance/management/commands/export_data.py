import json

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from grakon.utils import print_progress

class Command(BaseCommand):
    help = "Export data for analysis"

    def handle(self, *args, **options):
        from locations.models import Location
        from organizations.models import Organization
        from protocols.models import AttachedFile, Protocol
        from users.models import Role
        from violations.models import Violation

        locations_by_id = dict((location.id, location) for location in Location.objects.all())
        cik_protocols_by_location = dict((cp.location_id, cp) for cp in Protocol.objects.from_cik())

        violations_by_location = {}
        for violation in Violation.objects.all():
            violations_by_location.setdefault(violation.location_id, []).append(violation)

        organization_ct = ContentType.objects.get_for_model(Organization)
        organizations_by_id = dict((org.id, org) for org in Organization.objects.all())

        protocol_ct = ContentType.objects.get_for_model(Protocol)
        protocols_by_location = {}
        for protocol in Protocol.objects.from_users().filter(verified=True):
            protocols_by_location.setdefault(protocol.location_id, []).append(protocol)

        attachments_by_protocol = {}
        for af in AttachedFile.objects.all():
            if af.content_type_id==protocol_ct.id:
                attachments_by_protocol.setdefault(af.object_id, []).append(af.get_absolute_url())

        def protocol_to_json(protocol, is_cik):
            # TODO: add origin of protocol
            res = {}
            for attr in ('p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12',
                    'p13', 'p14', 'p15', 'p16', 'p17', 'p18', 'p19', 'p20', 'p21', 'p22', 'p23'):
                res[attr] = getattr(protocol, attr)

            if not is_cik:
                res['complaints'] = protocol.complaints
                if protocol.url:
                    res['media'] = [protocol.url]
                else:
                    res['media'] = attachments_by_protocol[protocol.id]

                if protocol.content_type_id == organization_ct.id:
                    res['source'] = organizations_by_id[protocol.object_id].name
                else:
                    res['source'] = 'grakon'

            return res

        def violation_to_json(violation):
            res = {}
            for attr in ('type', 'text', 'url'):
                res[attr] = getattr(violation, attr)

            if violation.content_type_id == organization_ct.id:
                res['source'] = organizations_by_id[violation.object_id].name
            else:
                res['source'] = 'grakon'

            return res

        def location_to_json(location):
            res = {'region': location.region_id, 'tik': location.tik_id}

            for attr in ('id', 'name', 'tvd', 'root', 'vrnorg', 'vrnkomis', 'x_coord',
                    'y_coord', 'region_code', 'region_name'):
                res[attr] = getattr(location, attr)

            if location.is_region():
                res['level'] = 'region'
            elif location.is_tik():
                res['level'] = 'tik'
            elif location.is_uik():
                res['level'] = 'uik'

            if location.id in cik_protocols_by_location:
                res['cik_data'] = protocol_to_json(cik_protocols_by_location[location.id], True)
            else:
                res['cik_data'] = {} # TODO: eliminate such locations

            res['protocols'] = [protocol_to_json(protocol, False) for protocol in protocols_by_location.get(location.id, [])]

            res['violations'] = [violation_to_json(violation) for violation in violations_by_location.get(location.id, [])]

            res['users'] = {}
            stats_data = json.loads(location.data)
            for role_type in ('voter', 'observer', 'journalist', 'member', 'lawyer'):
                res['users'][role_type] = stats_data.get(role_type, 0)

            return res

        data = [location_to_json(location) for location in locations_by_id.itervalues() if location.is_region()]
        data += [location_to_json(location) for location in locations_by_id.itervalues() if location.is_tik()]
        data += [location_to_json(location) for location in locations_by_id.itervalues() if location.is_uik()]

        from protocols.views import cloudfiles_conn

        protocols_container = cloudfiles_conn.get_container(settings.CLOUDFILES_CONTAINER)
        file_obj = protocols_container.create_object('dump.json')
        file_obj.content_type = 'application/json'
        file_obj.write(json.dumps(data, ensure_ascii=False).encode('utf8'), callback=print_progress)
