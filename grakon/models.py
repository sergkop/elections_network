# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

from loginza.models import UserMap
from tinymce.models import HTMLField

class Profile(models.Model):
    user = models.OneToOneField(User)
    username = models.CharField(max_length=30)
    first_name = models.CharField(u'Имя', max_length=30, default='')
    last_name = models.CharField(u'Фамилия', max_length=30, default='')
    middle_name = models.CharField(u'Отчество', max_length=30, blank=True, default='')
    show_name = models.BooleanField(u'Показывать настоящее имя', default=False,
            help_text=u'Если эта галка не выставлена, остальные пользователи будут видеть только ваше имя пользователя')
    about = HTMLField(u'О себе', default='', blank=True)

    @models.permalink
    def get_absolute_url(self):
        return ('profile', [self.username])

    def is_loginza_user(self):
        return UserMap.objects.filter(user=self.user).exists()

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

    def __unicode__(self):
        full_name = u'%s %s' % (self.first_name, self.last_name)
        return full_name.strip() or u'(Неизвестно)'

def create_profile(sender, **kwargs):
    if kwargs.get('created', False):
        profile = Profile()
        profile.user = kwargs['instance']
        profile.username = profile.user.username
        profile.save()

models.signals.post_save.connect(create_profile, sender=User)
