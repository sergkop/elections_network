# -*- coding:utf-8 -*-
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

class BaseRegistrationForm(forms.ModelForm):
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
    # TODO: do we need it?
    helper.form_id = 'registration_form'
    helper.layout = Layout(
        HTML(r'<input type="hidden" name="next" value="{% if next %}{{ next }}{% else %}{{ request.get_full_path }}{% endif %}" />'),
        HTML(r'<script type="text/javascript">$().ready(function(){  set_select_location("registration_form", []);});</script>'),
    )

    def __init__(self, *args, **kwargs):
        super(BaseRegistrationForm, self).__init__(*args, **kwargs)

        self.fields['region'].widget.choices = regions_list()

    def clean_tik(self):
        try:
            self.location = Location.objects.get(id=int(self.cleaned_data['tik']))
        except (ValueError, Location.DoesNotExist):
            raise forms.ValidationError(u'Выберите свой район')

        return self.cleaned_data['tik']

    def clean_password1(self):
        password = self.cleaned_data['password1']

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

class RegistrationForm(BaseRegistrationForm):
    def clean_username(self):
        try: 
            u = User.objects.get(username=self.cleaned_data['username'])
        except User.DoesNotExist: 
            return self.cleaned_data['username']

        raise forms.ValidationError(u'Пользователь с этим именем уже существует')

    def clean_email(self):
        try: 
            u = User.objects.get(email=self.cleaned_data['email'])
        except User.DoesNotExist: 
            return self.cleaned_data['email']

        raise forms.ValidationError(u'Пользователь с этим адресом электронной почты уже зарегистрирован')

    def save(self):
        user = ActivationProfile.objects.create_inactive_user(self.cleaned_data['username'],
                self.cleaned_data['email'], self.cleaned_data['password1'])

        profile = user.get_profile()
        profile.first_name = self.cleaned_data['first_name']
        profile.last_name = self.cleaned_data['last_name']
        profile.save()

        Role(user=profile, location=self.location, type='voter').save()

        return user

# TODO: fix it
class CompleteRegistrationForm(BaseRegistrationForm):
    # TODO: password fields must be optional (required=False)
    def __init__(self, user_id, *args, **kwargs):
        super(CompleteRegistrationForm, self).__init__(*args, **kwargs)
        self.user_id = user_id

        self.fields['password1'].mandatory = False
        self.fields['password2'].mandatory = False

    def clean_username(self):
        if self.cleaned_data['username']:
            try: 
                u = User.objects.exclude(id=self.user_id).get(username=self.cleaned_data['username'])
            except User.DoesNotExist: 
                u = None

            if u is not None:
                raise forms.ValidationError(u'Пользователь с этим именем уже зарегистрирован')
        return self.cleaned_data['username']

    def clean_email(self):
        if self.cleaned_data['email']:
            try: 
                u = User.objects.exclude(id=self.user_id).get(email=self.cleaned_data['email'])
            except User.DoesNotExist: 
                u = None

            if u is not None:
                raise forms.ValidationError(u'Пользователь с этим email уже зарегистрирован')
        return self.cleaned_data['email']
