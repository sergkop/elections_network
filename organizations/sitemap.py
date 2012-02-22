from django.contrib.sitemaps import Sitemap

from organizations.models import Organization

class OrganizationSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Organization.objects.filter(verified=True)
