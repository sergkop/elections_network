# -*- coding:utf-8 -*-
from django import forms

from grakon.utils import clean_html, form_helper
from organizations.models import Organization

class CreateOrganizationForm(forms.ModelForm):
    name = forms.RegexField(label=u'Идентификатор', max_length=20, min_length=2, regex=r'^[\w\.]+$',
            help_text=u'Идентификатор может содержать от 4 до 20 символов (латинские буквы, цифры, подчеркивания и точки).' \
                    u'<b>Этот идентификатор будет использован для формирования url страницы организации.</b>')

    helper = form_helper('', u'Создать')

    class Meta:
        model = Organization
        exclude = ('verified', 'is_partner', 'representative')

    def clean_about(self):
        return clean_html(self.cleaned_data['about'])

class EditOrganizationForm(forms.ModelForm):
    helper = form_helper('', u'Редактировать')

    class Meta:
        model = Organization
        exclude = ('verified', 'is_partner', 'name', 'signup_observers', 'teach_observers')

    def clean_about(self):
        return clean_html(self.cleaned_data['about'])
