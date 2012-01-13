from django.contrib.auth.models import User
from django.db import models

from geography.models import LocationModel

# TODO: add time_added field
class LinkModel(models.Model):
    location = models.ForeignKey(LocationModel)
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    url = models.URLField()

    class Meta:
        unique_together = ('url', 'location')

class ReportLinkModel(models.Model):
    user = models.ForeignKey(User)
    link = models.ForeignKey(LinkModel)

    class Meta:
        unique_together = ('user', 'link')
