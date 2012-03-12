from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from grakon.utils import print_progress

class Command(BaseCommand):
    help = "Recalculate protocols data at levels higher than uik. Argument is 'cik' or 'other'"

    def handle(self, *args, **options):
        from locations.models import Location
        from organizations.models import Organization
        from protocols.models import Protocol

        cik = Organization.objects.get(name='cik')
        content_type = ContentType.objects.get_for_model(Organization)

        if args[0] == 'cik':
            protocol_queryset = Protocol.objects.from_cik()
            organization = cik
        elif args[0] == 'other':
            protocol_queryset = Protocol.objects.verified()
            organization = Organization.objects.get(name='grakon')

        # TODO: take average if there are few protocols from one uik
        # Generate CIK data for TIKs
        j = 0
        tiks_count = Location.objects.exclude(region=None).filter(tik=None).count()
        for tik in Location.objects.exclude(region=None).filter(tik=None):
            protocols = list(protocol_queryset.filter(location__tik=tik))

            data = {'location': tik, 'verified': True}
            for i in range(23):
                data['p'+str(i+1)] = sum(getattr(protocol, 'p'+str(i+1)) for protocol in protocols)

            # a fix to renormalize weight of protocols
            #if args[0] == 'other':
            #    cik_protocol = Protocol.objects.from_cik().get(location=tik)
            #    if data['p10'] != 0:
            #        factor = float(cik_protocol.p10) / data['p10']
            #        for i in range(23):
            #            data['p'+str(i+1)] = int(factor*data['p'+str(i+1)])
            #    else:
            #        for i in range(23):
            #            data['p'+str(i+1)] = getattr(cik_protocol, 'p'+str(i+1))

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
            protocols = list(protocol_queryset.filter(location__region=region))

            data = {'location': region, 'verified': True}
            for i in range(23):
                data['p'+str(i+1)] = sum(getattr(protocol, 'p'+str(i+1)) for protocol in protocols)

            protocol, created = Protocol.objects.get_or_create(content_type=content_type,
                    object_id=organization.id, protocol_id=region.id, defaults=data)

            if not created:
                for i in range(23):
                    setattr(protocol, 'p'+str(i+1), data['p'+str(i+1)])
                protocol.save()
