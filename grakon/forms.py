# -*- coding:utf-8 -*-
from django import forms
from django.contrib.auth import authenticate
import django.contrib.auth.forms as auth_forms

from uni_form.layout import Hidden, HTML, Layout

from grakon.models import Profile
from grakon.utils import form_helper

class LoginForm(auth_forms.AuthenticationForm):
    helper = form_helper('login', u'Войти')
    helper.layout = Layout(HTML(
            r'<input type="hidden" name="next" value="{% if next %}{{ next }}{% else %}{{ request.get_full_path }}{% endif %}" />'))

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'username')

    helper = form_helper('edit_profile', u'Сохранить')

class SetPasswordForm(auth_forms.SetPasswordForm):
    helper = form_helper('set_password', u'Установить пароль')

class PasswordChangeForm(auth_forms.PasswordChangeForm):
    helper = form_helper('change_password', u'Сменить пароль')

class PasswordResetForm(auth_forms.PasswordResetForm):
    helper = form_helper('password_reset', u'Восстановить пароль')
