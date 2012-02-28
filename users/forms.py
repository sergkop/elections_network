# -*- coding:utf-8 -*-
from smtplib import SMTPException

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.forms.widgets import HiddenInput, Textarea, CheckboxInput
from django.template.loader import render_to_string

from uni_form.helper import FormHelper
from uni_form.layout import Submit

from users.models import ROLE_CHOICES, ROLE_TYPES
from grakon.utils import form_helper

class MessageForm(forms.Form):
    to_user = forms.ModelChoiceField(queryset=User.objects.all(), required=True, widget=HiddenInput())
    title = forms.CharField(required=False, label=u'Тема')
    body = forms.CharField(widget=Textarea(attrs={'cols':60, 'rows':4}), label=u'Сообщение')
    show_email = forms.BooleanField(label=u'Раскрыть получателю мой адрес электронной почты', initial=False, required=False)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.from_user = self.request.user
        super(MessageForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_action = reverse('send_message')
        self.helper.form_method = 'post'
        self.helper.form_id = 'send_message_form'

    def send(self):
        title = self.cleaned_data['title']
        title = u' '.join(title.split('\n'))
        body = self.cleaned_data['body']
        from_mail = settings.DEFAULT_FROM_EMAIL
        show_email = self.cleaned_data['show_email']
        to_user = self.cleaned_data['to_user']
        ctx = { 
            'title': title,
            'body': body,
            'show_email': show_email,
            'link': u'%s%s' % (settings.URL_PREFIX, reverse('profile', kwargs={'username': self.from_user.username})),
        }
        if show_email:
            ctx['from_user'] = self.from_user
        message = render_to_string('mail/notification.txt', ctx)
        mail_title = u'Пользователь %s написал вам сообщение' % self.from_user.username 
        try:
            send_mail(mail_title, message, from_mail, [to_user.email], fail_silently=False)
        except SMTPException:
            return u'Невозможно отправить сообщение'

class FeedbackForm(forms.Form):
    name = forms.CharField(label=u'Ваше имя')
    email = forms.CharField(label=u'Электронная почта')
    body = forms.CharField(widget=Textarea(attrs={'style': 'width:100%;'}), label=u'Сообщение')

    helper = form_helper('feedback', u'Отправить')

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(FeedbackForm, self).__init__(*args, **kwargs)
        if self.request.user.is_authenticated():
            del self.fields['name']
            del self.fields['email']

    def send(self):
        ctx = {
            'message': self.cleaned_data['body'],
            'user': self.request.user,
        }
        ctx['name'] = self.cleaned_data.get('name', '')
        ctx['email'] = self.cleaned_data.get('email', '')
        if self.request.user.is_authenticated():
            ctx['link']  = u'%s%s' % (settings.URL_PREFIX, reverse(
                    'profile', kwargs={'username': self.request.user.username}))
        from_mail = settings.DEFAULT_FROM_EMAIL
        message = render_to_string('feedback/mail.txt', ctx)
        send_mail(u'Сообщение обратной связи', message, from_mail, [from_mail], fail_silently=False)

class RoleTypeForm(forms.Form):
    type = forms.CharField(widget=forms.Select(choices=[('', u'Все типы участников')]+list(ROLE_CHOICES)))

    def clean_type(self):
        role_type = self.cleaned_data['type']
        if role_type!='' and role_type not in ROLE_TYPES:
            role_type = ''
        return role_type
