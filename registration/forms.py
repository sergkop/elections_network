# -*- coding:utf-8 -*-
import json
import re

from django import forms
from django.contrib.auth.models import User

from uni_form.layout import HTML, Layout

from grakon.models import Profile
from grakon.utils import form_helper
from locations.models import Location
from locations.utils import regions_list
from registration.models import ActivationProfile
from users.models import Role

try:
    from captcha.fields import CaptchaField
except ImportError:
    CaptchaField = None

password_digit_re = re.compile(r'\d')
password_letter_re = re.compile(r'[a-zA-Z]')

# TODO: do we need next hidden field?
layout = Layout(
    HTML(r'<input type="hidden" name="next" value="{% if next %}{{ next }}{% else %}{{ request.get_full_path }}{% endif %}" />'),
    HTML(r'<script type="text/javascript">' \
            '$().ready(function(){' \
                'set_select_location("registration_form", [{{ form.region.value|default:"" }}{% if form.tik.value %}, {{ form.tik.value }}{% endif %}]);' \
            '});' \
        '</script>'
    ),
)

class BaseRegistrationForm(forms.ModelForm):
    username = forms.RegexField(label=u'Имя пользователя (логин)', max_length=20, min_length=4, regex=r'^[\w\.]+$',
            help_text=u'Имя пользователя может содержать от 4 до 20 символов (латинские буквы, цифры, подчеркивания и точки).<br/>' \
                    u'<b>Под этим именем вас будут видеть другие пользователи, если вы не поставите галку ниже.</b>')

    region = forms.CharField(label=u'Выберите субъект РФ, где проживаете', widget=forms.Select(),
            help_text=u'Если вы находитесь за границей, выберите соответствующий пункт.')
    tik = forms.CharField(label=u'Выберите свой район', widget=forms.Select(choices=[('', u'Выберите свой район')]),
            help_text=u'Районы выделены по принципу отношения к территориальной избирательной комиссии')

    email = forms.EmailField(label=u'Электронная почта',
            help_text=u'На ваш электронный адрес будет выслано письмо со ссылкой для активации аккаунта')

    class Meta:
        model = Profile
        fields = ('username', 'last_name', 'first_name', 'show_name')

    def __init__(self, *args, **kwargs):
        """ if user_id is passed - loginza was used for registration """
        if 'user_map' in kwargs: # registred with loginza
            self.user_map = kwargs['user_map']
            del kwargs['user_map']
            self.user_id = self.user_map.user.id
        else:
            self.user_id = None

        super(BaseRegistrationForm, self).__init__(*args, **kwargs)

        if self.user_id:
            self.user_data = json.loads(self.user_map.identity.data)
            if self.user_data.get('email'):
                # TODO: if user with this email is already registered, it causes a problem
                self.fields['email'].widget = forms.HiddenInput()

        self.fields['region'].widget.choices = regions_list()

    def clean_username(self):
        try:
            # Exclude loginza-created user (if needed)
            User.objects.exclude(id=self.user_id).get(username=self.cleaned_data['username'])
        except User.DoesNotExist: 
            return self.cleaned_data['username']

        raise forms.ValidationError(u'Пользователь с этим именем уже существует')

    def clean_email(self):
        try: 
            User.objects.exclude(id=self.user_id).get(email=self.cleaned_data['email'])
        except User.DoesNotExist: 
            return self.cleaned_data['email']

        raise forms.ValidationError(u'Пользователь с этим адресом электронной почты уже зарегистрирован')

    def clean_tik(self):
        try:
            self.location = Location.objects.get(id=int(self.cleaned_data['tik']))
        except (ValueError, Location.DoesNotExist):
            raise forms.ValidationError(u'Выберите свой район')

        return self.cleaned_data['tik']

    def save(self):
        username, email, password = self.cleaned_data['username'], \
                self.cleaned_data['email'], self.cleaned_data.get('password1', '')

        if self.user_id:
            user = self.user_map.user
            user.username = username

            # if email is provided by loginza - use it (don't accept user's input - it's a security issue)
            user.email = self.user_data.get('email', email)

            user.set_password(password)
            user.save()
        else:
            # TODO: make sure email is still unique (use transaction)
            user = User.objects.create_user(username, email, password)

        profile = user.get_profile()
        for field in self.Meta.fields:
            setattr(profile, field, self.cleaned_data[field])
        profile.save()

        if self.user_id and self.user_data.get('email'): # email activation is not needed
            self.user_map.verified = True
            self.user_map.save()
            # TODO: send email just to notify of registration
        else:
            user.is_active = False
            user.save()
            ActivationProfile.objects.init_activation(user)

        Role.objects.get_or_create(type='voter', user=profile, defaults={'location': self.location})

        return user

class RegistrationForm(BaseRegistrationForm):
    password1 = forms.CharField(label=u'Пароль', widget=forms.PasswordInput(render_value=False),
            help_text=u'Пароль должен быть не короче <b>8 знаков</b> и содержать по крайней мере одну латинскую букву и одну цифру')
    password2 = forms.CharField(label=u'Подтвердите пароль', widget=forms.PasswordInput(render_value=False))

    helper = form_helper('register', u'Зарегистрироваться')
    helper.form_id = 'registration_form'
    helper.layout = layout

    if CaptchaField:
        captcha = CaptchaField(label=u'Код проверки', error_messages = {'invalid': u'Неверный код проверки'},
                help_text=u'Пожалуйста, введите цифры и буквы с картинки слева, чтобы мы могли отличить вас от робота')

    def clean_password1(self):
        password = self.cleaned_data['password1']

        if password != '':
            if len(password) < 8:
                raise forms.ValidationError(u'Пароль должен содержать не менее 8 символов')

            if password_letter_re.search(password) is None or password_digit_re.search(password) is None:
                raise forms.ValidationError(u'Пароль должен содержать по крайней мере одну латинскую букву и одну цифру')

        return password

    def clean_password2(self):
        password2 = self.cleaned_data['password2']
        if self.cleaned_data.get('password1', '') != self.cleaned_data['password2']:
            raise forms.ValidationError(u'Введенные вами пароли не совпадают')
        return password2

class LoginzaRegistrationForm(BaseRegistrationForm):
    helper = form_helper('loginza_register', u'Зарегистрироваться')
    helper.form_id = 'registration_form'
    helper.layout = layout
