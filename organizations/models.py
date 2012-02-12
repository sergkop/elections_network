# -*- coding:utf-8 -*-
from django.db import models

from locations.models import Location

class Organization(models.Model):
    name = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=50)
    about = HTMLField(u'Описание', default='')
    telephone = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    website = models.URLField(u'Сайт')
    email = models.CharField(max_length=100)
    representative = models.CharField(u'Контактное лицо', max_length=100)
    verified = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title

# TODO: do we need to introduce Location for Russia?
class OrganizationCoverage(models.Model):
    organization = models.ForeignKey(Location)
    location = models.ForeignKey(Organization)

    def __unicode__(self):
        return str(self.organization) + ': ' + str(self.location)
