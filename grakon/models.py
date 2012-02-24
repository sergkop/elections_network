# -*- coding:utf-8 -*-
import json
from random import choice
import string

from django.contrib.auth.models import User
from django.db import models

from loginza import signals
from loginza.conf import settings
from loginza.models import UserMap, UserMapManager
from tinymce.models import HTMLField

class Profile(models.Model):
    user = models.OneToOneField(User)
    username = models.CharField(max_length=30)
    first_name = models.CharField(u'Имя', max_length=30, default='')
    last_name = models.CharField(u'Фамилия', max_length=30, default='',
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
        full_name = u'%s %s' % (self.first_name, self.last_name)
        return full_name.strip() or self.username

def create_profile(sender, **kwargs):
    if kwargs.get('created', False):
        profile = Profile()
        profile.user = kwargs['instance']
        profile.username = profile.user.username
        profile.save()

models.signals.post_save.connect(create_profile, sender=User)

# Hack to fix bug in loginza
def new_for_identity(self, identity, request):
    try:
        user_map = self.get(identity=identity)
    except self.model.DoesNotExist:
        # if there is authenticated user - map identity to that user
        # if not - create new user and mapping for him
        if request.user.is_authenticated():
            user = request.user
        else:
            loginza_data = json.loads(identity.data)

            loginza_email = loginza_data.get('email', '')
            email = loginza_email if '@' in loginza_email else settings.DEFAULT_EMAIL

            # if nickname is not set - try to get it from email
            # e.g. vgarvardt@gmail.com -> vgarvardt
            loginza_nickname = loginza_data.get('nickname', None)
            username = loginza_nickname if loginza_nickname is not None else email.split('@')[0]

            # check duplicate user name
            while True:
                try:
                    existing_user = User.objects.get(username=username)
                    username = '%s%d%s' % (username, existing_user.id,
                            choice(string.letters)+choice(string.letters))
                except User.DoesNotExist:
                    break

            user = User.objects.create_user(username, email)

        user_map = UserMap.objects.create(identity=identity, user=user)
        signals.created.send(request, user_map=user_map)
    return user_map

UserMapManager.for_identity = new_for_identity
