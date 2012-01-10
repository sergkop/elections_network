from django.contrib.auth.models import User
from django.db import models

from geography.models import LocationModel

class LinkModel(models.Model):
    location = models.ForeignKey(LocationModel)
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    url = models.URLField()
