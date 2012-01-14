# coding=utf8
from django.contrib.auth.models import User
from django.db import models

from geography.models import LocationModel

#class ProfileModel(models.Model):
#    user = models.OneToOneField(User)

PARTICIPATION_TYPES = {
    'observer': u'Наблюдатель',
    'voter': u'Избиратель',
}

class ParticipationModel(models.Model):
    user = models.ForeignKey(User)
    location = models.ForeignKey(LocationModel)
    type = models.CharField(max_length=10)

    class Meta:
        unique_together = ('user', 'location', 'type')

    def type_name(self):
        return PARTICIPATION_TYPES[self.type]

# Friendship is a two-side non-commutable property
class FriendsModel(models.Model):
    user1 = models.ForeignKey(User, related_name='user1')
    user2 = models.ForeignKey(User, related_name='user2')

    class Meta:
        unique_together = ('user1', 'user2')
