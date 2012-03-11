# -*- coding:utf-8 -*-
import json
from random import choice
import string

from django.contrib.auth.models import User
from django.db import models

from loginza import signals
from loginza.conf import settings
from loginza.models import UserMap
from tinymce.models import HTMLField

class Profile(models.Model):
    user = models.OneToOneField(User)
    username = models.CharField(max_length=30)
    first_name = models.CharField(u'Имя', max_length=30, default='', blank=True)
    last_name = models.CharField(u'Фамилия', max_length=30, default='', blank=True,
            help_text=u'<b>Мы не будем показывать ваше настоящее имя другим пользователям без вашего разрешения.</b>')
    middle_name = models.CharField(u'Отчество', max_length=30, blank=True, default='')
    show_name = models.BooleanField(u'Показывать настоящее имя', default=False,
            help_text=u'<b>Поставьте эту галку чтобы другие пользователи видели ваше настоящее имя</b>' \
                    u' (к участникам, открывающим свои имена, больше доверия на площадке)')
    about = HTMLField(u'О себе', default='', blank=True)

    @models.permalink
    def get_absolute_url(self):
        return ('profile', [self.username])

    def is_loginza_user(self):
        return UserMap.objects.filter(user=self.user).exists()

    def has_name(self):
        return self.first_name and self.last_name

    """
    def update_from_identity(self, identity):
        try:
            data = json.loads(identity.data)
        except ValueError:
            return
        data = data.get('name', None)
        if data is None:
            return 
        if 'full_name' in data:
            self.last_name = data['full_name']
        if 'last_name' in data:
            self.last_name = data['last_name']
        if 'first_name' in data:
            self.first_name = data['first_name'] 
        self.save()
    """

    def points(self):
        count = 0

        if self.has_name():
            count += 1

        if self.show_name:
            count += 2

        if self.about:
            count += 2

        return count

    def __unicode__(self):
        if self.show_name and self.first_name and self.last_name:
            return u'%s %s (%s)' % (self.first_name, self.last_name, self.username)
        return self.username

def create_profile(sender, **kwargs):
    if kwargs.get('created', False):
        profile = Profile()
        profile.user = kwargs['instance']
        profile.username = profile.user.username
        profile.save()

models.signals.post_save.connect(create_profile, sender=User)
