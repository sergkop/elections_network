from django.contrib.auth.models import User
from django.db import models

from geography.models import Location

# TODO: add time_added field
class Link(models.Model):
    location = models.ForeignKey(Location)
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    url = models.URLField()

    class Meta:
        unique_together = ('url', 'location')

class ReportLink(models.Model):
    user = models.ForeignKey(User)
    link = models.ForeignKey(Link)

    class Meta:
        unique_together = ('user', 'link')
