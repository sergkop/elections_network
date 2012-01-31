# coding=utf8
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

from links.models import Link

# 'other' reason is added at the end of each block later
REPORT_REASONS = {
    'user': [
        ('user_insult', u'Оскорбительное поведение'),
        ('user_spam', u'Спам'),
    ],
    'link': [
        ('link_does_not_exist', u'Ссылка на несуществующий ресурс'),
        ('link_not_related', u'Ресурс, не связанный с выборами'),
        ('link_wrong_place', u'Ресурс не относящийся к региону'),
        ('link_wrong_title', u'Название ссылки не отражает ее содержание'),
        ('link_duplicate', u'Ссылка дублирует уже существующую'),
    ],
}

OTHER_REASON = ('other', u'Другая причина')

# [(reason: title)]
REASON_CHOICES = []
for reasons in REPORT_REASONS.values():
    REASON_CHOICES += reasons
REASON_CHOICES.append(OTHER_REASON)

# {type: {reason: title}}
REASON_TYPES = {}
for name in REPORT_REASONS:
    REPORT_REASONS[name].append(OTHER_REASON)
    REASON_TYPES[name] = dict(REPORT_REASONS[name])

MODELS = {
    'user': User,
    'link': Link,
}

# Content types
# content_type.name gives the type name of the item ('user', 'link', etc.)
#CONTENT_TYPES = dict((name, ContentType.objects.get_for_model(model)) for name, model in MODELS.items())

class ReportManager(models.Manager):
    # TODO: cache the results of this query (memcached)
    def user_reports(self, user):
        reports = list(super(ReportManager, self).filter(reporter=user))

        res = {}
        for name, model in MODELS.iteritems():
            content_type = ContentType.objects.get_for_model(model)
            model_reports = filter(lambda report: report.content_type_id==content_type.id, reports)
            object_ids = map(lambda model_report: model_report.object_id, model_reports)
            if object_ids:
                queryset = model.objects.filter(id__in=object_ids)

                if name == 'user':
                    res[name] = queryset.values_list('username', flat=True)
                elif name == 'link':
                    res[name] = queryset.values_list('location_id', 'url')
            else:
                res[name] = []

        return res

class Report(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    item = generic.GenericForeignKey('content_type', 'object_id')

    reporter = models.ForeignKey(User, related_name='users_who_reported')
    reason = models.CharField(max_length=15, choices=REASON_CHOICES)
    reason_explained = models.TextField()
    time = models.DateTimeField(auto_now=True)

    objects = ReportManager()

    class Meta:
        unique_together = ('content_type', 'object_id', 'reporter')
