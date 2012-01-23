# -*- coding:utf-8 -*-
from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import User

class RegistrationForm(auth_forms.UserCreationForm):
    username = forms.RegexField(label="Имя пользователя", max_length=30,
            min_length=4, required=True, regex=r'^[\w.@+-]+$')
    email = forms.EmailField()
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтвердите пароль", widget=forms.PasswordInput)
    first_name = forms.CharField(label="Имя")
    last_name = forms.CharField(label="Фамилия")

    def clean_username(self):
        if self.cleaned_data['username']:
            try: 
                u = User.objects.get(username=self.cleaned_data['username'])
            # if username is unique - it's ok
            except User.DoesNotExist: 
                u = None

            if u is not None:
                raise forms.ValidationError(u'Пользователь с этим именем уже зарегистрирован')
        return self.cleaned_data['username']

    def clean_email(self):
        if self.cleaned_data['email']:
            try: 
                u = User.objects.get(email=self.cleaned_data['email'])
            # if email is unique - it's ok
            except User.DoesNotExist: 
                u = None

            if u is not None:
                raise forms.ValidationError(u'Пользователь с этим email уже зарегистрирован')
        return self.cleaned_data['email']
