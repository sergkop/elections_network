# -*- coding:utf-8 -*-
from django.db import models

from tinymce.models import HTMLField

from locations.models import Location

class Organization(models.Model):
    name = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=50)
    about = HTMLField(u'Описание', default='')
    telephone = models.CharField(u'Телефон', max_length=50, blank=True)
    address = models.CharField(u'Адрес', max_length=200, blank=True)
    website = models.URLField(u'Сайт', blank=True)
    email = models.CharField(u'Электронная почта', max_length=100, blank=True)
    representative = models.CharField(u'Контактное лицо', max_length=100, blank=True)

    verified = models.BooleanField(default=False)
    is_partner = models.BooleanField(default=False)

    signup_observers = models.BooleanField(u'Запись в наблюдатели', default=False)
    teach_observers = models.BooleanField(u'Обучение наблюдателей', default=False)

    def __unicode__(self):
        return self.title

    # TODO: implement it
    def covers_location(self, location):
        if not location.region_id:
            pass
        elif not location.tik_id:
            pass

class OrganizationCoverage(models.Model):
    location = models.ForeignKey(Location, blank=True, null=True)
    organization = models.ForeignKey(Organization)

    class Meta:
        unique_together = ('organization', 'location')

    def __unicode__(self):
        return unicode(self.organization) + ': ' + unicode(self.location)
