from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from scrapy.selector import HtmlXPathSelector

from grakon.utils import print_progress, read_url

class Command(BaseCommand):
    help = "Import election results from cikrf.ru"

    def handle(self, *args, **options):
        from locations.models import Location
        from organizations.models import Organization
        from protocols.models import Protocol

        cik = Organization.objects.get(name='cik')
        content_type = ContentType.objects.get_for_model(Organization)

        locations_processed = Protocol.objects.filter(content_type=content_type, object_id=cik.id) \
                .values_list('location', flat=True)
        uiks_count = Location.objects.exclude(tik=None).count()
        j = len(locations_processed)
        for location in Location.objects.exclude(tik=None).exclude(id__in=locations_processed):
            trs = HtmlXPathSelector(text=read_url(location.results_url())) \
                    .select("//table[@width='100%' and @cellspacing='1' and @cellpadding='2' and @bgcolor='#ffffff']//tr")
            #trs = list(HtmlXPathSelector(text=read_url(location.results_url())) \
            #        .select("//body//table[3]//tr[4]//td//table[6]//tr"))

            del trs[18]
            assert len(trs) == 23, "incorrect number of rows"

            data = {}
            for i in range(23):
                data['p'+str(i+1)] = int(trs[i].select(".//b/text()").extract()[0])

            data.update({'location': location, 'verified': True})

            Protocol.objects.get_or_create(content_type=content_type, object_id=cik.id,
                    protocol_id=location.id, defaults=data)

            print_progress(j, uiks_count)
            j += 1

