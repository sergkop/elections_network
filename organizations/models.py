# -*- coding:utf-8 -*-
from django.db import models
from django.db.models import Q

from tinymce.models import HTMLField

from locations.models import Location

# TODO: increase max_length of title
# TODO: limit name format
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

    # TODO: implement it
    def covers_location(self, location):
        if not location.region_id:
            pass
        elif not location.tik_id:
            pass

    @models.permalink
    def get_absolute_url(self):
        return ('organization_info', (), {'name': self.name})

    def __unicode__(self):
        return self.title

class OrganizationCoverageManager(models.Manager):
    # TODO: cache this function on a short period (10 min)
    def organizations_at_location(self, location):
        """ Generates required data for right side Organization block only """
        if location is None:
            queryset = self.filter(location=None)
        elif location.region is None:
            queryset = self.filter(Q(location=None) | Q(location=location))
        elif location.tik is None:
            queryset = self.filter(Q(location=None) | Q(location__id__in=[location.region_id, location.id]))
        else:
            queryset = self.filter(Q(location=None) | Q(location__id__in=[location.tik_id, location.region_id, location.id]))

        organization_ids = set(queryset.values_list('organization_id', flat=True))

        return Organization.objects.filter(id__in=organization_ids).only(
                'name', 'title', 'signup_observers', 'teach_observers', 'verified', 'is_partner')

class OrganizationCoverage(models.Model):
    location = models.ForeignKey(Location, blank=True, null=True)
    organization = models.ForeignKey(Organization)

    objects = OrganizationCoverageManager()

    class Meta:
        unique_together = ('organization', 'location')

    def __unicode__(self):
        return unicode(self.organization) + ': ' + unicode(self.location)
