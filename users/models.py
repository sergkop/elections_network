# -*- coding:utf-8 -*-
from django.db import models

from grakon.models import Profile
from locations.models import Location
from organizations.models import Organization

ROLE_CHOICES = (
    ('observer', u'Наблюдатель'),
    ('voter', u'Избиратель'),
    ('journalist', u'Представитель СМИ'),
    ('lawyer', u'Юрист'),
    ('prosecutor', u'Представитель прокуратуры'),
    ('member', u'Член избирательной комиссии'),
    ('authority', u'Представитель власти'),
    ('supporter', u'Поддержка наблюдателей'),
)
ROLE_TYPES = dict(ROLE_CHOICES)

class RoleManager(models.Manager):
    def get_participants(self, query):
        participants = {}

        roles_by_type = {}
        for role_id, role_type in list(self.filter(query).values_list('id', 'type')):
            roles_by_type.setdefault(role_type, []).append(role_id)

        role_ids = []
        for role_type in roles_by_type:
            # TODO: Temporary hack
            role_ids += roles_by_type[role_type][:10]

        for role in list(Role.objects.filter(id__in=role_ids).select_related('user', 'organization')):
            participants.setdefault(role.type, []).append(role)

        # Sort participants by name and limit the length of the lists
        for role in participants:
            show_name_participants = filter(lambda p: p.user.show_name, participants[role])
            other_participants = filter(lambda p: not p.user.show_name, participants[role])

            participants[role] = sorted(show_name_participants, key=lambda r: r.user.username.lower())
            participants[role] += sorted(other_participants, key=lambda r: r.user.username.lower())

        return participants

class Role(models.Model):
    user = models.ForeignKey(Profile, related_name='roles')
    location = models.ForeignKey(Location)
    type = models.CharField(max_length=10, choices=ROLE_CHOICES, db_index=True)

    organization = models.ForeignKey(Organization, blank=True, null=True, db_index=True)
    data = models.CharField(max_length=200, default='', blank=True)
    verified = models.BooleanField(default=False, db_index=True)

    time = models.DateTimeField(auto_now=True)

    objects = RoleManager()

    class Meta:
        unique_together = ('user', 'location', 'type')

    def type_name(self):
        return ROLE_TYPES[self.type]

    def __unicode__(self):
        return unicode(self.user) + ' is ' + self.type + ' at ' + unicode(self.location)

class Contact(models.Model):
    user = models.ForeignKey(Profile, related_name='contacts')
    contact = models.ForeignKey(Profile, related_name='have_in_contacts')
    time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'contact')

    def __unicode__(self):
        return unicode(self.user) + ' has ' + unicode(self.contact) + ' in contacts'

MEMBER_CHOICES = (
    ('chairman', u'Председатель'),
    ('vice', u'Заместитель председателя'),
    ('secretary', u'Секретарь'),
    ('prg', u'Член с правом решающего голоса'),
    ('psg', u'Член с правом совещательного голоса'),
    ('other', u'Другое'),
)

PARTY_CHOICES = (
    ('ER', u'Единая Россия'),
    ('KPRF', u'КПРФ'),
    ('LDPR', u'ЛДПР'),
    ('SR', u'Справедливая Россия'),
    ('Prohorov', u'Штаб Прохорова'),
    ('Yabloko', u'Яблоко'),
    ('other', u'Другое'),
)

class Message(models.Model):
    from_user = models.ForeignKey(Profile, verbose_name=u'От пользователя', related_name='sender')
    to_user = models.ForeignKey(Profile, verbose_name=u'Пользователю', related_name='reciever')
    title = models.CharField(u'Тема', max_length=100)
    body = models.TextField(u'Сообщение')
    show_email = models.BooleanField(u'Показывать email', default=False)
    time = models.DateTimeField(auto_now=True)

class CommissionMember(models.Model):
    last_name = models.CharField(u'Фамилия', max_length=50)
    first_name = models.CharField(u'Имя', max_length=50)
    middle_name = models.CharField(u'Отчество', max_length=50, blank=True)
    role = models.CharField(u'Должность', max_length=100, choices=MEMBER_CHOICES)
    party = models.CharField(u'Кем выдвинут', max_length=100, choices=PARTY_CHOICES)
    job = models.CharField(u'Место работы', max_length=100, blank=True)

    user = models.ForeignKey(Profile)
    location = models.ForeignKey(Location)
    time = models.DateTimeField(auto_now=True)

class WebObserver(models.Model):
    start_time = models.IntegerField(u'Начало наблюдения', help_text=u'Местное время')
    end_time = models.IntegerField(u'Окончание наблюдения')
    capture_video = models.BooleanField(u'Будет ли производиться захват видео', default=False)
    url = models.URLField(u'Ссылка на видео', blank=True)

    user = models.ForeignKey(Profile)
    location = models.ForeignKey(Location)
    time = models.DateTimeField(auto_now=True)

class UnsubscribedUser(models.Model):
    user = models.ForeignKey(Profile, unique=True)
    time = models.DateTimeField(auto_now=True)
