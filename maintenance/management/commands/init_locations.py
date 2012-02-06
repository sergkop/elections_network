from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Loads locations data after first syncdb."

    def handle(self, *args, **options):
        from locations.models import Location
        from navigation.models import Page
