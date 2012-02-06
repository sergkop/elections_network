# -*- coding:utf-8 -*-
from django import forms
from django.contrib.auth.models import User

from uni_form.layout import HTML, Layout

from grakon.models import Profile
from grakon.utils import form_helper
from registration.models import ActivationProfile

class BaseRegistrationForm(forms.ModelForm):
    username = forms.RegexField(label=u'Имя пользователя', max_length=20, min_length=4, regex=r'^\w+$',
            help_text=u'Имя пользователя может содержать от 4 до 20 символов (латинские буквы, цифры и подчеркивания)')
    email = forms.EmailField(label=u'Электронная почта')
    password1 = forms.CharField(label=u'Пароль', widget=forms.PasswordInput(render_value=False),
            help_text=u'Пароль должен быть не короче 8 знаков и содержать по крайней мере одну букву, одну цифру и знак препинания')
    password2 = forms.CharField(label=u'Подтвердите пароль', widget=forms.PasswordInput(render_value=False))

    class Meta:
        model = Profile
        fields = ('username', 'first_name', 'middle_name', 'last_name', 'show_name')

    helper = form_helper('register', u'Зарегистрироваться')
    # TODO: do we need it?
    helper.layout = Layout(HTML(
            r'<input type="hidden" name="next" value="{% if next %}{{ next }}{% else %}{{ request.get_full_path }}{% endif %}" />'))

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

        return user

# TODO: fix it
class CompleteRegistrationForm(forms.Form):
    # TODO: password fields must be optional (required=False)
    def __init__(self, user_id, *args, **kwargs):
        super(CompleteRegistrationForm, self).__init__(*args, **kwargs)
        self.user_id = user_id

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
