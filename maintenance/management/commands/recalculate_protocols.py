import sys

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

def print_progress(i, count):
    """ Show progress message updating in-place """
    if i < count-1:
        sys.stdout.write("\r%(percent)2.3f%%" % {'percent': 100*float(i)/count})
        sys.stdout.flush()
    else:
        sys.stdout.write("\r")
        sys.stdout.flush()

class Command(BaseCommand):
    help = "Recalculate protocols data at levels higher than uik. Argument is 'cik' or 'other'"

    def handle(self, *args, **options):
        from locations.models import Location
        from organizations.models import Organization
        from protocols.models import Protocol

        cik = Organization.objects.get(name='cik')
        content_type = ContentType.objects.get_for_model(Organization)

        if args[0] == 'cik':
            protocol_queryset = Protocol.objects.filter(content_type=content_type, object_id=cik.id)
            organization = cik
        elif args[0] == 'other':
            protocol_queryset = Protocol.objects.exclude(content_type=content_type, object_id=cik.id)
            organization = Organization.objects.get(name='grakon')

        # TODO: take average if there are few protocols from one uik
        # Generate CIK data for TIKs
        j = 0
        tiks_count = Location.objects.exclude(region=None).filter(tik=None).count()
        for tik in Location.objects.exclude(region=None).filter(tik=None):
            protocols = list(protocol_queryset.filter(location__tik=tik).filter(verified=True))

            data = {'location': tik, 'verified': True}
            for i in range(23):
                data['p'+str(i+1)] = sum(getattr(protocol, 'p'+str(i+1)) for protocol in protocols)

            protocol, created = Protocol.objects.get_or_create(content_type=content_type,
                    object_id=organization.id, protocol_id=tik.id, defaults=data)

            if not created:
                for i in range(23):
                    setattr(protocol, 'p'+str(i+1), data['p'+str(i+1)])
                protocol.save()

            print_progress(j, tiks_count)
            j += 1

        # Generate CIK data for regions
        for region in Location.objects.filter(region=None):
            protocols = list(protocol_queryset.filter(location__region=region).filter(verified=True))

            data = {'location': region, 'verified': True}
            for i in range(23):
                data['p'+str(i+1)] = sum(getattr(protocol, 'p'+str(i+1)) for protocol in protocols)

            protocol, created = Protocol.objects.get_or_create(content_type=content_type,
                    object_id=organization.id, protocol_id=region.id, defaults=data)

            if not created:
                for i in range(23):
                    setattr(protocol, 'p'+str(i+1), data['p'+str(i+1)])
                protocol.save()