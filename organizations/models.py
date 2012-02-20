# -*- coding:utf-8 -*-
from django.db import models
from django.db.models import Q
from grakon.models import Profile
from locations.models import Location
from tinymce.models import HTMLField



class OrganizationManager(models.Manager):
    pass

# TODO: increase max_length of title
# TODO: limit name format
# TODO: drop exclude field?
class Organization(models.Model):
    title = models.CharField(u'Название', max_length=50)
    name = models.CharField(u'Идентификатор', max_length=30, unique=True)
    about = HTMLField(u'Описание', default='')
    telephone = models.CharField(u'Телефон', max_length=50, blank=True)
    address = models.CharField(u'Адрес', max_length=200, blank=True)
    website = models.URLField(u'Сайт', help_text=u'Адрес сайта должен начинаться с http:// или https://')
    email = models.CharField(u'Электронная почта', max_length=100, blank=True)
    representative = models.CharField(u'Контактное лицо', max_length=100, blank=True)

    verified = models.BooleanField(default=False)
    is_partner = models.BooleanField(default=False)

    signup_observers = models.BooleanField(u'Запись в наблюдатели', default=False,
            help_text=u'Укажите помогает ли ваша организация записаться в наблюдатели')
    teach_observers = models.BooleanField(u'Обучение наблюдателей', default=False,
            help_text=u'Укажите занимается ли ваша организация обучением наблюдателей')

    signup_journalists = models.BooleanField(u'Запись в представителей СМИ', default=False,
            help_text=u'Укажите помогает ли ваша организация записаться в представители СМИ')
    observer_coordination = models.BooleanField(u'Координация групп наблюдения', default=False)
    mobile_groups = models.BooleanField(u'Мобильные группы', default=False)
    signup_lawyers = models.BooleanField(u'Юридическая помощь', default=False,
            help_text=u'Укажите оказывает ли ваша организация юридическую помощь')
    news_publishing = models.BooleanField(u'Публикация новостей', default=False)
    elections_info = models.BooleanField(u'Распространение информации о выборах', default=False)
    
    objects = OrganizationManager()

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
    
    def get_representatives(self):
        return self.organizationrepresentative_set.all()
        return OrganizationRepresentative.objects.filter(organization=self).values_list('user', flat=True)
    
    def get_representative_profiles(self):
        representatives = self.get_representatives().values_list('user', flat=True)
        profiles = Profile.objects.filter(id__in=representatives)
        return profiles
    
    def get_locations(self):
        location_ids =  self.organizationcoverage_set.values_list('location_id', flat=True)
        locations = Location.objects.filter(id__in=location_ids).select_related()
        if None in location_ids:
            locations.append(None) # special processing for the whole country
        return locations

    def get_verified_roles(self):
        return self.role_set.filter(verified=True)
    
    def get_unverified_roles(self):
        return self.role_set.filter(verified=False)
    
    def get_observers(self):
        roles = self.get_verified_roles().filter(type = 'observer').values_list('user', flat=True)
        return Profile.objects.filter(pk__in = roles)

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

        return Organization.objects.filter(id__in=organization_ids).order_by('title').only(
                'name', 'title', 'signup_observers', 'teach_observers', 'verified', 'is_partner')

class OrganizationCoverage(models.Model):
    location = models.ForeignKey(Location, blank=True, null=True)
    organization = models.ForeignKey(Organization)

    objects = OrganizationCoverageManager()

    class Meta:
        unique_together = ('organization', 'location')

    def __unicode__(self):
        return unicode(self.organization) + ': ' + unicode(self.location)

class OrganizationRepresentative(models.Model):
    organization = models.ForeignKey(Organization)
    user = models.ForeignKey(Profile)
    time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('organization', 'user')

    def __unicode__(self):
        return unicode(self.organization) + ': ' + unicode(self.user)
