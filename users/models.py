# -*- coding:utf-8 -*-
from django.db import models

from grakon.models import Profile
from locations.models import Location
from organizations.models import Organization

ROLE_CHOICES = (
    ('observer', u'Наблюдатель'),
    ('voter', u'Избиратель'),
    ('journalist', u'Представитель СМИ'),
    ('lawyer', u'Юрист'),
    ('prosecutor', u'Представитель прокуратуры'),
    ('member', u'Член избирательной комиссии'),
    ('authority', u'Представитель власти'),
)
ROLE_TYPES = dict(ROLE_CHOICES)

class RoleManager(models.Manager):
    # TODO: do we need it?
    def get_user_roles(self, user):
        res = {}
        for role in self.filter(user=user):
            res[role.type] = role
        return res

class Role(models.Model):
    user = models.ForeignKey(Profile, related_name='roles')
    location = models.ForeignKey(Location)
    type = models.CharField(max_length=10, choices=ROLE_CHOICES)

    organization = models.ForeignKey(Organization, blank=True, null=True)
    data = models.CharField(max_length=200, default='', blank=True)
    verified = models.BooleanField(default=False)

    time = models.DateTimeField(auto_now=True)

    objects = RoleManager()

    class Meta:
        unique_together = ('user', 'location', 'type')

    def type_name(self):
        return ROLE_TYPES[self.type]

    def __unicode__(self):
        return unicode(self.user) + ' is ' + self.type + ' at ' + unicode(self.location)

class Contact(models.Model):
    user = models.ForeignKey(Profile, related_name='contacts')
    contact = models.ForeignKey(Profile, related_name='have_in_contacts')
    time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'contact')

    def __unicode__(self):
        return unicode(self.user) + ' has ' + unicode(self.contact) + ' in contacts'
