# -*- coding:utf-8 -*-
from django import forms
from django.contrib.auth.models import User

class CompleteRegistrationForm(forms.Form):
    username = forms.RegexField(max_length=30, min_length=4, required=True, regex=r'^[\w.@+-]+$')
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(widget=forms.PasswordInput, required=False)
    first_name = forms.CharField()
    last_name = forms.CharField()

    def __init__(self, user_id, *args, **kwargs):
        super(CompleteRegistrationForm, self).__init__(*args, **kwargs)
        self.user_id = user_id

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
