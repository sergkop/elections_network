# -*- coding:utf-8 -*-
from django import forms

from uni_form.helper import FormHelper
from uni_form.layout import Submit

from grakon.models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'username')

    helper = FormHelper()
    helper.form_action = 'edit_profile'
    helper.form_method = 'POST'
    helper.add_input(Submit('', u'Сохранить'))
