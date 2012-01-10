# coding=utf8
from django.contrib.auth.models import User
from django.db import models

from geography.models import LocationModel

#class ProfileModel(models.Model):
#    user = models.OneToOneField(User)

PARTICIPATION_TYPES = {
    'nabl': u'Наблюдатель',
    'izbr': u'Избиратель',
}

class ParticipationModel(models.Model):
    user = models.ForeignKey(User)
    location = models.ForeignKey(LocationModel)
    type = models.CharField(max_length=10)

    def type_name(self):
        return PARTICIPATION_TYPES[self.type]
