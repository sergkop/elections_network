from django.contrib.sitemaps import Sitemap

from locations.models import Location

class LocationSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        # TODO: add tik level as well
        return Location.objects.filter(region=None)
