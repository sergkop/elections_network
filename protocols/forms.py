# -*- coding:utf-8 -*-
from django import forms

from uni_form.layout import HTML, Layout

from grakon.utils import form_helper
from locations.models import Location
from locations.utils import regions_list
from protocols.models import Protocol

# TODO: check control sums
class ProtocolForm(forms.ModelForm):
    region = forms.CharField(label=u'Выберите субъект РФ', widget=forms.Select())
    tik = forms.CharField(label=u'Выберите ТИК', widget=forms.Select(choices=[('', u'Выберите ТИК')]))
    uik = forms.CharField(label=u'Выберите УИК', widget=forms.Select(choices=[('', u'Выберите УИК')]))

    photo1 = forms.FileField(label=u'Фотография')
    photo2 = forms.FileField(label=u'Фотография', required=False)
    photo3 = forms.FileField(label=u'Фотография', required=False)
    photo4 = forms.FileField(label=u'Фотография', required=False)
    photo5 = forms.FileField(label=u'Фотография', required=False)

    class Meta:
        model = Protocol
        exclude = ('content_type', 'object_id', 'protocol_id', 'location', 'url', 'verified')

    helper = form_helper('', u'Сохранить')
    helper.form_id = 'upload_protocol_form'
    helper.layout = Layout(
        HTML(r'<script type="text/javascript">' \
                '$().ready(function(){' \
                    'set_select_location("upload_protocol_form", [{{ location.region_id|default:"" }}{% if location.tik_id %}, {{ location.tik_id }}{% endif %}, {{ location.id }}]);' \
                '});' \
            '</script>'
        ),
    )

    def __init__(self, *args, **kwargs):
        super(ProtocolForm, self).__init__(*args, **kwargs)
        self.fields['region'].widget.choices = regions_list()
        for field in ('chairman', 'assistant', 'secretary', 'number', 'sign_time', 'recieve_time', 'complaints'):
            self.fields[field].required = True

    def clean_uik(self):
        try:
            self.location = Location.objects.get(id=int(self.cleaned_data.get('uik', '')))
        except (ValueError, Location.DoesNotExist):
            raise forms.ValidationError(u'Неверно выбран УИК')
        return self.cleaned_data['uik']

    def clean(self):
        total = sum(self.cleaned_data[field] for field in ('p19', 'p20', 'p21', 'p22', 'p23'))
        if self.cleaned_data['p10'] != total:
            raise forms.ValidationError(u'Число голосов в поле 10 не совпадает с суммой полей 9, 19, 20, 21, 22, 23')

        if self.cleaned_data['p7']+self.cleaned_data['p8'] != self.cleaned_data['p9']+self.cleaned_data['p10']:
            raise forms.ValidationError(u'Сумма чисел в полях 7 и 8  не совпадает с суммой полей 9 и 10')

        if self.cleaned_data['p1'] < self.cleaned_data['p3']+self.cleaned_data['p4']+self.cleaned_data['p5']:
            raise forms.ValidationError(u'Число в поле 1 должно быть не меньше, чем сумма полей 3, 4, 5')

        if self.cleaned_data['p2']+self.cleaned_data['p18'] < self.cleaned_data['p3']+self.cleaned_data['p4']+self.cleaned_data['p5']+self.cleaned_data['p6']+self.cleaned_data['p17']:
            raise forms.ValidationError(u'Число в поле 1 должно быть не меньше, чем сумма полей 3, 4, 5')

        return self.cleaned_data

    def save(self):
        protocol = super(ProtocolForm, self).save(commit=False)
        protocol.location = self.location
        return protocol
