import sys

from django.core.management.base import BaseCommand

def print_progress(i, count):
    """ Show progress message updating in-place """
    if i < count-1:
        sys.stdout.write("\r%(percent)2.1f%%" % {'percent': 100*float(i)/count})
        sys.stdout.flush()
    else:
        sys.stdout.write("\r")
        sys.stdout.flush()

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
