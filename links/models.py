# coding=utf8
from django.contrib.auth.models import User
from django.db import models

from locations.models import Location

class Link(models.Model):
    location = models.ForeignKey(Location)
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    url = models.URLField()
    time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('url', 'location')

    def __unicode__(self):
        return self.url
