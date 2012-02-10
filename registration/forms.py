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

password_digit_re = re.compile(r'\d')
password_letter_re = re.compile(r'[a-zA-Z]')

class RegistrationForm(forms.ModelForm):
    username = forms.RegexField(label=u'Имя пользователя (логин)', max_length=20, min_length=4, regex=r'^[\w\.]+$',
            help_text=u'Имя пользователя может содержать от 4 до 20 символов (латинские буквы, цифры, подчеркивания и точки)')

    region = forms.CharField(label=u'Выберите субъект РФ, где проживаете', widget=forms.Select(),
            help_text=u'Если вы находитесь за границей, выберите соответствующий пункт.')
    tik = forms.CharField(label=u'Выбирите свой район', widget=forms.Select(choices=[('', u'Выберите свой район')]),
            help_text=u'Районы выделены по принципу отношения к территориальной избирательной комиссией')

    email = forms.EmailField(label=u'Электронная почта')
    password1 = forms.CharField(label=u'Пароль', widget=forms.PasswordInput(render_value=False),
            help_text=u'Пароль должен быть не короче 8 знаков и содержать по крайней мере одну латинскую букву и одну цифру')
    password2 = forms.CharField(label=u'Подтвердите пароль', widget=forms.PasswordInput(render_value=False))

    class Meta:
        model = Profile
        fields = ('username', 'last_name', 'first_name', 'middle_name', 'show_name')

    helper = form_helper('register', u'Зарегистрироваться')
    # TODO: do we need next hidden field?
    helper.form_id = 'registration_form'
    helper.layout = Layout(
        HTML(r'<input type="hidden" name="next" value="{% if next %}{{ next }}{% else %}{{ request.get_full_path }}{% endif %}" />'),
        HTML(r'<script type="text/javascript">$().ready(function(){  set_select_location("registration_form", []);});</script>'),
    )

    def __init__(self, *args, **kwargs):
        """ if user_id is passed - loginza was used for registration """
        if 'user_map' in kwargs: # registred with loginza
            self.user_map = kwargs['user_map']
            del kwargs['user_map']
            self.user_id = self.user_map.user.id
        else:
            self.user_id = None

        super(RegistrationForm, self).__init__(*args, **kwargs)

        if self.user_id:
            self.fields['password1'].required = False
            self.fields['password2'].required = False

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

    def save(self):
        username, email, password = self.cleaned_data['username'], \
                self.cleaned_data['email'], self.cleaned_data["password1"]

        if self.user_id:
            user = self.user_map.user
            user.username = username
            user.email = email
            user.set_password(password)
        else:
            # TODO: make sure email is still unique (use transaction)
            user = User.objects.create_user(username, email, password)

        activation_needed = True
        if self.user_id:
            user_data = json.loads(self.user_map.identity.data)
            if user_data.get('email') == email:
                activation_needed = False

        if activation_needed:
            user.is_active = False
            ActivationProfile.objects.init_activation(user)
        else:
            self.user_map.verified = True
            self.user_map.save()
            # TODO: send email just to notify of registration

        user.save()

        profile = user.get_profile()
        for field in self.Meta.fields:
            setattr(profile, field, self.cleaned_data[field])
        profile.save()

        Role.objects.get_or_create(type='voter', user=profile, defaults={'location': self.location})

        return user

class LoginzaRegistrationForm(RegistrationForm):
    # TODO: code duplication (because helper's action is different)
    helper = form_helper('loginza_register', u'Зарегистрироваться')
    # TODO: do we need next hidden field?
    helper.form_id = 'registration_form'
    helper.layout = Layout(
        HTML(r'<input type="hidden" name="next" value="{% if next %}{{ next }}{% else %}{{ request.get_full_path }}{% endif %}" />'),
        HTML(r'<script type="text/javascript">$().ready(function(){  set_select_location("registration_form", []);});</script>'),
    )
