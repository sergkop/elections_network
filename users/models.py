# coding=utf8
from django.contrib.auth.models import User
from django.db import models

from tinymce.models import HTMLField

from locations.models import Location

class Profile(models.Model):
    user = models.OneToOneField(User)
    middle_name = models.CharField(max_length=30)
    about = HTMLField()

ROLE_CHOICES = (
    ('observer', u'Наблюдатель'),
    ('voter', u'Избиратель'),
)
ROLE_TYPES = dict(ROLE_CHOICES)

class Role(models.Model):
    user = models.ForeignKey(User)
    location = models.ForeignKey(Location)
    type = models.CharField(max_length=10, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'location', 'type')

    def type_name(self):
        return ROLE_TYPES[self.type]

class Contact(models.Model):
    user = models.ForeignKey(User, related_name='users')
    contact = models.ForeignKey(User, related_name='contacts')

    class Meta:
        unique_together = ('user', 'contact')

def create_profile(sender, **kwargs):
    if kwargs.get('created', False):
        profile = Profile()
        profile.user = kwargs['instance']
        profile.save()

models.signals.post_save.connect(create_profile, sender=User)
