# -*- coding:utf-8 -*-
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

from locations.models import Location

VIOLATION_CHOICES = (
    ('1', u'Ограничение прав наблюдателя'),
    ('2', u'Необоснованное удаление с участка'),
    ('3', u'Вброс бюллетеней'),
    ('4', u'Массовая доставка избирателей на участок'),
    ('5', u'Групповое голосование по открепительным'),
    ('6', u'Давление начальства на избирателей'),
    ('7', u'Подкуп'),
    ('8', u'Непредоставление права голоса'),
    ('9', u'Незаконная агитация'),
    ('10', u'Нарушение на выездном голосовании'),
    ('11', u'Присутствие на участке посторонних лиц'),
    ('12', u'Нарушение правил подведения итогов'),
    ('13', u'Искажение результатов'),
    ('14', u'Невыдача копии протокола'),
    ('15', u'Другое'),
)

class Violation(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    source = generic.GenericForeignKey('content_type', 'object_id')

    violation_id = models.IntegerField(u'Идентификатор')
    type = models.CharField(u'Тип нарушения', max_length=15, choices=VIOLATION_CHOICES)
    text = models.TextField(u'Сообщение')
    location = models.ForeignKey(Location)
    time = models.DateTimeField(auto_now=True)
    url = models.URLField(u'Ссылка', blank=True, help_text=u'Ссылка на доказательства')

    class Meta:
        unique_together = ('content_type', 'object_id', 'violation_id')

    @models.permalink
    def get_absolute_url(self):
        return ('violation_view', (), {'violation_id': self.id})
