# coding=utf8
from django.db import models

from grakon.models import Profile
from locations.models import Location

class Link(models.Model):
    location = models.ForeignKey(Location)
    user = models.ForeignKey(Profile, related_name='links')
    name = models.CharField(max_length=200)
    url = models.URLField()
    time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('url', 'location')

    def __unicode__(self):
        return self.url
