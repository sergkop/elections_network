# coding=utf8
from django.contrib.auth.models import User
from django.db import models

from geography.models import Location

class Link(models.Model):
    location = models.ForeignKey(Location)
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    url = models.URLField()
    time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('url', 'location')

    def __unicode__(self):
        return self.url

LINK_REPORT_CHOICES = (
    ('not_exist', u'Ссылка на несуществующий ресурс'),
    ('not_related', u'Ресурс, не связанный с выборами'),
    ('wrong_place', u'Ресурс не относящийся к региону'),
    ('wrong_title', u'Название ссылки не отражает ее содержание'),
    ('duplicate', u'Ссылка дублирует уже существующую'),
    ('other', u'Другая причина'),
)
LINK_REPORT_TYPES = dict(LINK_REPORT_CHOICES)

class ReportLink(models.Model):
    user = models.ForeignKey(User)
    link = models.ForeignKey(Link)
    reason = models.CharField(max_length=15, choices=LINK_REPORT_CHOICES)
    reason_explained = models.TextField()
    time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'link')
