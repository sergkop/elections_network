# -*- coding:utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

from grakon.utils import cache_function
from locations.models import Location
from organizations.models import Organization

@cache_function('cik_and_grakon', 600)
def cik_and_grakon():
    return {
        'cik': Organization.objects.get(name='cik'),
        'grakon': Organization.objects.get(name='grakon'),
        'content_type': ContentType.objects.get_for_model(Organization),
    }

class ProtocolManager(models.Manager):
    def from_cik(self):
        data = cik_and_grakon()
        return self.filter(content_type=data['content_type'], object_id=data['cik'].id)

    def verified(self):
        data = cik_and_grakon()
        return self.exclude(content_type=data['content_type'], object_id=data['cik'].id) \
                .filter(verified=True)

    def from_users(self):
        data = cik_and_grakon()
        return self.exclude(content_type=data['content_type'],
                object_id__in=[data['cik'].id, data['grakon'].id])

class Protocol(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    source = generic.GenericForeignKey('content_type', 'object_id')

    protocol_id = models.IntegerField(u'Идентификатор')

    chairman = models.CharField(u'Ф.И.О. председателя комиссии', max_length=150, blank=True)
    assistant = models.CharField(u'Ф.И.О. заместителя председателя комиссии', max_length=150, blank=True)
    secretary = models.CharField(u'Ф.И.О. секретаря комиссии', max_length=150, blank=True)
    number = models.IntegerField(u'Номер копии протокола, полученного наблюдателем', blank=True, null=True,
            help_text=u'Указан вверху первой страницы')
    sign_time = models.DateTimeField(u'Время подписи', null=True, blank=True, help_text=u'В формате "2011-04-25 14:30"')
    recieve_time = models.DateTimeField(u'Время выдачи', null=True, blank=True, help_text=u'В формате "2011-04-25 14:30"')

    p1 = models.IntegerField(u'1. Число избирателей, включенных в список избирателей на момент окончания голосования')
    p2 = models.IntegerField(u'2. Число избирательных бюллетеней, полученных участковой избирательной комиссией')
    p3 = models.IntegerField(u'3. Число избирательных бюллетеней, выданных избирателям, проголосовавшим досрочно')
    p4 = models.IntegerField(u'4. Число избирательных бюллетеней, выданных участковой избирательной комиссией избирателям в помещении для голосования в день голосования')
    p5 = models.IntegerField(u'5. Число избирательных бюллетеней, выданных избирателям, проголосовавшим вне помещения для голосования в день голосования')
    p6 = models.IntegerField(u'6. Число погашенных избирательных бюллетеней')
    p7 = models.IntegerField(u'7. Число избирательных бюллетеней, содержащихся в переносных ящиках для голосования')
    p8 = models.IntegerField(u'8. Число избирательных бюллетеней, содержащихся в стационарных ящиках для голосования')
    p9 = models.IntegerField(u'9. Число недействительных избирательных бюллетеней')
    p10 = models.IntegerField(u'10. Число действительных избирательных бюллетеней')
    p11 = models.IntegerField(u'11. Число открепительных удостоверений, полученных участковой избирательной комиссией')
    p12 = models.IntegerField(u'12. Число открепительных удостоверений, выданных участковой избирательной комиссией избирателям на избирательном участке до дня голосования')
    p13 = models.IntegerField(u'13. Число избирателей, проголосовавших по открепительным удостоверениям на избирательном участке')
    p14 = models.IntegerField(u'14. Число неиспользованных открепительных удостоверений')
    p15 = models.IntegerField(u'15. Число открепительных удостоверений, выданных избирателям территориальной избирательной комиссией')
    p16 = models.IntegerField(u'16. Число утраченных открепительных удостоверений')
    p17 = models.IntegerField(u'17. Число утраченных избирательных бюллетеней')
    p18 = models.IntegerField(u'18. Число избирательных бюллетеней, не учтенных при получении')
    p19 = models.IntegerField(u'19. Число голосов, поданных за Жириновского В.В.')
    p20 = models.IntegerField(u'20. Число голосов, поданных за Зюганова Г.А.')
    p21 = models.IntegerField(u'21. Число голосов, поданных за Миронова С.М.')
    p22 = models.IntegerField(u'22. Число голосов, поданных за Прохорова М.Д.')
    p23 = models.IntegerField(u'23. Число голосов, поданных за Путина В.В.')

    location = models.ForeignKey(Location)
    complaints = models.IntegerField(u'Количество поступивших жалоб', null=True, blank=True)
    time = models.DateTimeField(auto_now=True)
    url = models.URLField(u'Ссылка на фотографию', blank=True) # TODO: depricate it

    verified = models.BooleanField(default=False, db_index=True)

    objects = ProtocolManager()

    class Meta:
        unique_together = ('content_type', 'object_id', 'protocol_id')

    @models.permalink
    def get_absolute_url(self):
        return ('protocol_view', (), {'protocol_id': self.id})

# TODO: override delete method and remove files
class AttachedFile(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    item = generic.GenericForeignKey('content_type', 'object_id')

    internal = models.BooleanField(default=False)
    url = models.URLField(u'Ссылка') # url or filename for internal files

    def get_absolute_url(self):
        if self.internal:
            return settings.CLOUDFILES_URL_PREFIX + self.url
        else:
            return self.url
