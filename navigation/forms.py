# -*- coding:utf-8 -*-
from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import User


class RegistrationForm(auth_forms.UserCreationForm):
    username = forms.RegexField(label="Имя пользователя", max_length=30,
            min_length=4, required=True, regex=r'^[\w.@+-]+$')
    email = forms.EmailField()
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтвердите пароль",
                                widget=forms.PasswordInput)
    first_name = forms.CharField(label="Имя")
    last_name = forms.CharField(label="Фамилия")

    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        if username:
            try:
                cur_user = User.objects.get(username=username)
            except User.DoesNotExist:
                cur_user = None

            if cur_user:
                raise forms.ValidationError(
                            u'Пользователь с таким логином уже существует')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        if email:
            try:
                cur_user = User.objects.get(email=self.cleaned_data['email'])
            # if email is unique - it's ok
            except User.DoesNotExist:
                cur_user = None

            if cur_user:
                raise forms.ValidationError(
                            u'Пароли не совпадают')
        return email

    def clean_passowrd2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 == password2:
            raise forms.ValidationError(
                   'Ввёденный вами, повтороный пароль, не совпадает с первым')
        return password2
