# -*- coding:utf-8 -*-
from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import User

class RegistrationForm(auth_forms.UserCreationForm):
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField()
    last_name = forms.CharField()

    def clean_username(self):
        if self.cleaned_data['username']:
            try: 
                u = User.objects.exclude(id=self.user_id).get(username=self.cleaned_data['username'])
            # if username is unique - it's ok
            except User.DoesNotExist: 
                u = None

            if u is not None:
                raise forms.ValidationError(u'Пользователь с этим именем уже зарегистрирован')
        return self.cleaned_data['username']

    def clean_email(self):
        if self.cleaned_data['email']:
            try: 
                u = User.objects.exclude(id=self.user_id).get(email=self.cleaned_data['email'])
            # if email is unique - it's ok
            except User.DoesNotExist: 
                u = None

            if u is not None:
                raise forms.ValidationError(u'Пользователь с этим email уже зарегистрирован')
        return self.cleaned_data['email']
