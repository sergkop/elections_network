# -*- coding:utf-8 -*-
from django import forms
from django.forms.widgets import HiddenInput
from grakon.utils import clean_html, form_helper
from locations.models import Location
from locations.utils import regions_list
from organizations.models import Organization
from uni_form.layout import HTML, Layout
from users.models import Role



class CreateOrganizationForm(forms.ModelForm):
    name = forms.RegexField(label=u'Идентификатор', max_length=20, min_length=2, regex=r'^[\w\.]+$',
            help_text=u'Идентификатор может содержать от 4 до 20 символов (латинские буквы, цифры, подчеркивания и точки).' \
                    u'<b>Этот идентификатор будет использован для формирования url страницы организации.</b>')

    region = forms.CharField(label=u'Выберите субъект РФ, где работает ваша организация', widget=forms.Select(),
            help_text=u'Оставьте поле незаполненным, если ваша организация работает по всей стране', required=False)
    tik = forms.CharField(label=u'Выберите район', widget=forms.Select(choices=[('', u'Выберите район')]),
            help_text=u'<b>Оставьте поле незаполненным, если ваша организация работает во всем субъекте</b><br/>' \
                    u'Если ваша организация работает в нескольких районах, напишите нам письмо на admin@grakon.org с указанием этого.' \
                    u'При этом укажите названия районов как они указаны на нашем сайте.', required=False)

    helper = form_helper('', u'Создать')
    helper.form_id = 'create_organization_form'
    helper.layout = Layout(
        HTML(r'<script type="text/javascript">' \
                '$().ready(function(){' \
                    'set_select_location("create_organization_form", [{{ form.region.value|default:"" }}{% if form.tik.value %}, {{ form.tik.value }}{% endif %}]);' \
                '});' \
            '</script>'
        ),
    )

    class Meta:
        model = Organization
        exclude = ('verified', 'is_partner', 'representative')

    def __init__(self, *args, **kwargs):
        super(CreateOrganizationForm, self).__init__(*args, **kwargs)
        self.fields['region'].widget.choices = regions_list()

    def clean_name(self):
        try:
            Organization.objects.get(name=self.cleaned_data['name'])
        except Organization.DoesNotExist:
            return self.cleaned_data['name']
        raise forms.ValidationError(u'Организация с таким идентификатором уже существует')

    def clean_about(self):
        return clean_html(self.cleaned_data['about'])

    def clean(self):
        try:
            self.location = Location.objects.get(id=int(self.cleaned_data.get('tik', '')))
        except (ValueError, Location.DoesNotExist):
            try:
                self.location = Location.objects.get(id=int(self.cleaned_data.get('region', '')))
            except (ValueError, Location.DoesNotExist):
                self.location = None

        return self.cleaned_data

class EditOrganizationForm(forms.ModelForm):
    helper = form_helper('', u'Редактировать')

    class Meta:
        model = Organization
        fields = ('title', 'about', 'telephone', 'address', 'website', 'email')

    def clean_about(self):
        return clean_html(self.cleaned_data['about'])
    
class VerificationForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['verified']
        
    def __init__(self, request, *args, **kwargs):
        super(VerificationForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['verified'].widget = HiddenInput()
        
    def clean(self):
        profile = self.request.user.profile
        if not profile.is_representative(self.instance.organization):
            raise forms.ValidationError(u'Вы не представитель организации')
        return self.cleaned_data