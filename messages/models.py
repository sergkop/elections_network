from django.db import models

from grakon.models import Profile

"""
class Message(models.Model):
    from_user = models.ForeignKey(u'Пользователю', Profile)
    to_user = models.ForeignKey(u'От пользователя', Profile)
    title = models.CharField(u'Тема')
    body = models.TextField(u'Сообщение')
    show_email = models.BooleanField(u'Показывать email')
    time = models.DateTimeField(auto_now=True)
"""