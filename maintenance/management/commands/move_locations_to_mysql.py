from django.core.management.base import BaseCommand

from grakon.utils import print_progress

class Command(BaseCommand):
    help = "Move locations data to mysql."

    def handle(self, *args, **options):
        from locations.models import Location

        print "creating regions"
        for location in Location.objects.filter(region=None):
            location.save(using='default1')

        print "creating tiks"
        i = 0
        uik_count = Location.objects.filter(tik=None).exclude(region=None).count()
        for location in Location.objects.filter(tik=None).exclude(region=None):
            print_progress(i, uik_count)
            location.save(using='default1')
            i += 1

        print "creating uiks"
        i = 0
        uik_count = Location.objects.exclude(tik=None).count()
        for location in Location.objects.exclude(tik=None):
            print_progress(i, uik_count)
            location.save(using='default1')
            i += 1
