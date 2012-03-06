from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from lxml.etree import fromstring

from grakon.utils import read_url

GN_TO_GRAKON = {
    '1': '2',
    '2': '1',
    '3': '3',
    '4': '5',
    '5': '10',
    '6': '1',
    '7': '1',
    '8': '11',
    '9': '12',
    '10': '12',
    '11': '1',
    '12': '14',
    '13': '1',
    '14': '1',
    '15': '1',
    '16': '15',
    '17': '15',
    '18': '9',
    '19': '15',
    '20': '1',
    '21': '15',
    '22': '4',
    '23': '15',
    '24': '5',
    '25': '6',
    '26': '1',
    '27': '10',
    '28': '1',
    '29': '1',
    '30': '12',
    '31': '12',
    '32': '12',
    '33': '12',
    '34': '12',
    '35': '15',
    '36': '15',
}

class Command(BaseCommand):
    help = "Import violations"

    def handle(self, *args, **options):
        from locations.models import Location
        from organizations.models import Organization
        from violations.models import Violation

        organization = Organization.objects.get(name='nabludatel')
        content_type = ContentType.objects.get_for_model(Organization)

        xml = fromstring(read_url('http://gnhq.info/export/violations.xml', encoding=None))
        for viol_xml in xml:
            data = {}
            for field in viol_xml:
                if field.tag == 'id':
                    data['id'] = int(field.text)
                elif field.tag == 'updt':
                    data['time'] = datetime.strptime(field.text, '%y-%m-%d %H:%M')
                elif field.tag == 'obscomment':
                    data['text'] = field.text or ''
                elif field.tag == 'region':
                    data['region'] = int(field.text) # coincides with our projection
                elif field.tag == 'uik':
                    data['uik'] = field.text
                elif field.tag == 'type':
                    data['type'] = GN_TO_GRAKON[field.text]

            # Try to get location
            try:
                location = Location.objects.get(region_code=data['region'], name=data['uik'])
            except Location.DoesNotExist:
                print "Failed to find location of violation " + str(data['id'])
                continue

            violation, created = Violation.objects.get_or_create(content_type=content_type, object_id=organization.id,
                    violation_id=data['id'], defaults={'text': data['text'],
                    'url': '', 'type': data['type'], 'location': location,
            })

            if not created:
                violation.text = data['text']
                violation.url = ''
                violation.type = data['type']
                violation.save()
