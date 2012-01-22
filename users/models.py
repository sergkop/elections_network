# coding=utf8
from django.contrib.auth.models import User
from django.db import models

from geography.models import Location

class Profile(models.Model):
    user = models.OneToOneField(User)
    about = models.TextField()

PARTICIPATION_TYPES = {
    'observer': u'Наблюдатель',
    'voter': u'Избиратель',
}

class Participation(models.Model):
    user = models.ForeignKey(User)
    location = models.ForeignKey(Location)
    type = models.CharField(max_length=10)

    class Meta:
        unique_together = ('user', 'location', 'type')

    def type_name(self):
        return PARTICIPATION_TYPES[self.type]

class Contact(models.Model):
    user = models.ForeignKey(User, related_name='users')
    contact = models.ForeignKey(User, related_name='contacts')

    class Meta:
        unique_together = ('user', 'contact')

class ReportUser(models.Model):
    user = models.ForeignKey(User, related_name='reported_users')
    reporter = models.ForeignKey(User, related_name='reporters')

    class Meta:
        unique_together = ('user', 'reporter')

def create_profile(sender, **kwargs):
    if kwargs.get('created', False):
        profile = Profile()
        profile.user = kwargs['instance']
        profile.save()

models.signals.post_save.connect(create_profile, sender=User)
