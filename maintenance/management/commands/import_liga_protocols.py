from django.core.management.base import BaseCommand

from scrapy.selector import HtmlXPathSelector

from grakon.utils import print_progress, read_url

LIST_URL = 'https://svodnyprotokol.ru/zapros.php?fed=0&uik=&type=paper&narush_type=no&shtab=0'

class Command(BaseCommand):
    help = "Import prorocols from Svodny Protocol"

    def handle(self, *args, **options):
        from locations.models import Location
        from organizations.models import Organization
        from protocols.models import Protocol

        liga = Organization.objects.get(name='liga')
        content_type = ContentType.objects.get_for_model(Organization)

        HtmlXPathSelector(text=read_url(LIST_URL)) \
                    .select("//div[@class='page_navigation'][0]//a")
