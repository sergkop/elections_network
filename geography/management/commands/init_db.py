import os.path

from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """ Temporary operation """
    help = "Loads geography data after first syncdb."

    def handle(self, *args, **options):
        from geography.models import LocationModel

        for line in open(os.path.join(settings.PROJECT_PATH, 'regions.txt')).readlines():
            try:
                name = line[:-1].decode('utf8')
            except:
                print line[:-1]
            
            LocationModel.objects.create(name=name)
