from django.contrib.auth.models import User
from django.db import models

from geography.models import LocationModel

#class ProfileModel(models.Model):
#    user = models.OneToOneField(User)

class ParticipationModel(models.Model):
    user = models.ForeignKey(User)
    location = models.ForeignKey(LocationModel)
    type = models.CharField(max_length=10)
