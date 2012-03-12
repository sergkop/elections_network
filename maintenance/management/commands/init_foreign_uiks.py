import os.path

from django.conf import settings
from django.core.management.base import BaseCommand

from scrapy.selector import HtmlXPathSelector

from grakon.utils import print_progress, read_url

FOREIGN_UIKS_URL = 'http://www.foreign-countries.vybory.izbirkom.ru/region/region/foreign-countries?action=show&root=1000085&tvd=100100032124923&vrn=100100031793505&region=99&global=true&sub_region=99&prver=0&pronetvd=null&vibid=100100032124923&type=226'

class Command(BaseCommand):
    help = "Init foreign uiks"

    def handle(self, *args, **options):
        from locations.models import FOREIGN_CODE, FOREIGN_NAME, Location

        uiks = {}
        for line in open(os.path.join(settings.PROJECT_PATH, 'data', 'foreign_uiks.csv'), 'r'):
            uik_no, country_id, country_name, address = line.strip().split(',')
            uiks[uik_no] = {'tik': int(country_id), 'address': address}

        countries_by_id = dict((location.id, location) for location in Location.objects.exclude(region=None) \
                .filter(tik=None).filter(region_code=FOREIGN_CODE))

        foreign_countries = Location.objects.get(region=None, region_code=FOREIGN_CODE)

        i = 0
        for uik_option in HtmlXPathSelector(text=read_url(FOREIGN_UIKS_URL)) \
                .select("//select[@name='gs']//option"):
            uik_no = uik_option.select("text()").extract()[0].strip()[:4]

            if uik_no not in uiks:
                print uik_no
                continue

            url = uik_option.select("@value").extract()[0]
            for param in url.split('?')[1].split('&'):
                param_name, param_value = param.split('=')
                if param_name in ('root', 'tvd'):
                    uiks[uik_no][param_name] = int(param_value)

            location = Location(region=foreign_countries, tik=countries_by_id[uiks[uik_no]['tik']],
                    name=uik_no, region_name=FOREIGN_NAME, region_code=FOREIGN_CODE,
                    address=uiks[uik_no]['address'], tvd=uiks[uik_no]['tvd'],
                    root=uiks[uik_no]['root'], data='{}')
            #location.save()

            i += 1
            print_progress(i, 350)

        print uiks
