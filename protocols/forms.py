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

    photo1 = forms.FileField(label=u'Фотография', help_text=u'Если суммарный размер закачиваемых файлов составляет <b>несколько мегабайт</b>, может потребоваться предварительная архивация файлов.')
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
        for field in ('chairman', 'assistant', 'secretary', 'sign_time', 'complaints'):
            self.fields[field].required = True

    def clean_uik(self):
        try:
            self.location = Location.objects.get(id=int(self.cleaned_data.get('uik', '')))
        except (ValueError, Location.DoesNotExist):
            raise forms.ValidationError(u'Неверно выбран УИК')
        return self.cleaned_data['uik']

    def clean(self):
        data = dict(('p'+str(i), self.cleaned_data.get('p'+str(i), 0)) for i in range(1, 24))

        if data['p10'] != data['p19'] + data['p20'] + data['p21'] + data['p22'] + data['p23']:
            raise forms.ValidationError(u'Число голосов в поле 10 не совпадает с суммой полей 19, 20, 21, 22, 23')

        if data['p7']+data['p8'] != data['p9']+data['p10']:
            raise forms.ValidationError(u'Сумма чисел в полях 7 и 8  не совпадает с суммой полей 9 и 10')

        if data['p1'] < data['p3']+data['p4']+data['p5']:
            raise forms.ValidationError(u'Число в поле 1 должно быть не меньше, чем сумма полей 3, 4, 5')

        if data['p2']+data['p18'] < data['p3']+data['p4']+data['p5']+data['p6']+data['p17']:
            raise forms.ValidationError(u'Число в поле 1 должно быть не меньше, чем сумма полей 3, 4, 5')

        return self.cleaned_data

    def save(self):
        protocol = super(ProtocolForm, self).save(commit=False)
        protocol.location = self.location
        return protocol
