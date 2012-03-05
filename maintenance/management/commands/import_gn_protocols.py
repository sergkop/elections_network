from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from lxml.etree import fromstring

class Command(BaseCommand):
    help = "First argument must be xml file from http://gnhq.info/export/protocols.xml"

    def handle(self, *args, **options):
        from locations.models import Location
        from organizations.models import Organization
        from protocols.models import Protocol

        organization = Organization.objects.get(name='nabludatel')
        content_type = ContentType.objects.get_for_model(Organization)

        xml = fromstring(open(args[0], 'r').read())
        for protocol_xml in xml:
            data = {}
            numbers = {}
            for field in protocol_xml:
                if field.tag == 'id':
                    data['id'] = int(field.text)
                elif field.tag == 'ncomp':
                    data['complaints'] = int(field.text)
                elif field.tag == 'region':
                    data['region'] = int(field.text) # coincides with our projection
                elif field.tag == 'uik':
                    data['uik'] = field.text
                elif field.tag == 'updt':
                    if field.text.startswith('11'): # hack to fix GN bug
                        field.text = '12'+field.text[:2]
                    data['sign_time'] = datetime.strptime(field.text, '%y-%m-%d %H:%M')
                elif field.tag == 'media':
                    if len(field) != 1:
                        raise ValueError
                    data['url'] = list(field)[0].text

                if field.tag.startswith('p'):
                    try:
                        p_index = int(field.tag[1:])
                    except ValueError:
                        continue

                    if p_index<1 or p_index>23:
                        continue

                    numbers[field.tag] = int(field.text)

            # Try to get location
            try:
                location = Location.objects.get(region_code=data['region'], name=data['uik'])
            except Location.DoesNotExist:
                print "Failed to find location of violation " + str(data['id'])
                continue

            if 'url' not in data:
                continue # skip protocols without images

            numbers.update({'url': data['url'], 'location': location,
                    'sign_time': data.get('sign_time'), 'complaints': data.get('complaints')})

            Protocol.objects.get_or_create(content_type=content_type, object_id=organization.id,
                    protocol_id=data['id'], defaults=numbers)
