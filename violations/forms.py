# -*- coding:utf-8 -*-
from random import choice

from django import forms

from uni_form.layout import HTML, Layout

from grakon.utils import form_helper
from locations.models import Location
from locations.utils import regions_list
from violations.models import Violation

class ViolationForm(forms.ModelForm):
    region = forms.CharField(label=u'Выберите субъект РФ', widget=forms.Select(),
            help_text=u'Выберите местоположение нарушения')
    tik = forms.CharField(label=u'Выберите ТИК', widget=forms.Select(choices=[('', u'Выберите ТИК')]),
            help_text=u'Не вводите ничего, если нарушение произошло на уровне субъекта РФ', required=False)
    uik = forms.CharField(label=u'Выберите УИК', widget=forms.Select(choices=[('', u'Выберите УИК')]),
            help_text=u'Не вводите ничего, если нарушение произошло на уровне ТИК', required=False)

    class Meta:
        model = Violation
        fields = ('type', 'text', 'url')

    helper = form_helper('', u'Сохранить')
    helper.form_id = 'edit_violation_form'
    helper.layout = Layout(
        HTML(r'<script type="text/javascript">' \
                '$().ready(function(){' \
                    'set_select_location("edit_violation_form", [{{ violation.location.region_id|default:"" }}{% if violation.location.tik_id %}, {{ violation.location.tik_id }}{% endif %}, {{ violation.location.id }}]);' \
                '});' \
            '</script>'
        ),
    )

    def __init__(self, *args, **kwargs):
        super(ViolationForm, self).__init__(*args, **kwargs)
        self.fields['region'].widget.choices = regions_list()

    def clean(self):
        try:
            self.location = Location.objects.get(id=int(self.cleaned_data.get('uik', '')))
        except (ValueError, Location.DoesNotExist):
            try:
                self.location = Location.objects.get(id=int(self.cleaned_data.get('tik', '')))
            except (ValueError, Location.DoesNotExist):
                try:
                    self.location = Location.objects.get(id=int(self.cleaned_data.get('region', '')))
                except (ValueError, Location.DoesNotExist):
                    raise forms.ValidationError(u'Неверно выбран избирательный округ')

        return self.cleaned_data

    def save(self, commit=True):
        violation = super(ViolationForm, self).save(commit=False)
        violation.violation_id = choice(range(1000))
        violation.location = self.location
        if commit:
            violation.save()
        return violation
