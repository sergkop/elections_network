from django import forms

from locations.models import Location

# TODO: it is currently not used
class RegionForm(forms.Form):
    region = forms.CharField(label=u'Выберите субъект РФ, где проживаете', widget=forms.Select(),
            help_text=u'Если вы находитесь за границей, выберите соответствующий пункт.')
    tik = forms.CharField(label=u'Выберите свой район', widget=forms.Select(choices=[('', u'Выберите свой район')]),
            help_text=u'Районы выделены по принципу отношения к территориальной избирательной комиссии')
    uik = forms.CharField(label=u'Выберите свой участокы', widget=forms.Select(choices=[('', u'Выберите свой участок')]))

    #HTML(r'<script type="text/javascript">' \
    #        '$().ready(function(){' \
    #            'set_select_location("registration_form", [{{ form.region.value|default:"" }}{% if form.tik.value %}, {{ form.tik.value }}{% endif %}]);' \
    #        '});' \
    #    '</script>'
    #),

    def clean(self):
        try:
            self.location = Location.objects.exclude(tik=None).get(id=int(self.cleaned_data['uik']))
        except (ValueError, Location.DoesNotExist):
            try:
                self.location = Location.objects.get(id=int(self.cleaned_data['tik']))
            except (ValueError, Location.DoesNotExist):
                self.location = None

            #raise forms.ValidationError(u'Выберите свой район')

        return self.cleaned_data

    #Role.objects.get_or_create(type='voter', user=profile, defaults={'location': self.location})
