import json
from urllib import quote

from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms.widgets import Media

from users.models import Contact
from reports.models import Report, REPORT_REASONS

def user_data(request):
    context = {
        'REPORT_REASONS': json.dumps(REPORT_REASONS, ensure_ascii=False),
        #'VK_APP_ID': settings.VK_APP_ID,
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
        'YA_METRIKA_ID': settings.YA_METRIKA_ID,
        'DISQUS_SHORTNAME': settings.DISQUS_SHORTNAME,
        'YANDEX_MAPS_KEY': settings.YANDEX_MAPS_KEY,
        'URL_PREFIX': settings.URL_PREFIX,
    }
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        context['my_profile'] = profile
        context['CONTACTS'] = json.dumps(list(profile.contacts.values_list('contact__username', flat=True)))
        print Report.objects.user_reports(profile), type(Report.objects.user_reports(profile))
        context['REPORTS'] = json.dumps(Report.objects.user_reports(profile))
    else:
        if request.path is not None and request.path not in settings.LOGINZA_AMNESIA_PATHS:
            request.session['loginza_return_path'] = request.path

        context['CONTACTS'] = '[]'
        context['REPORTS'] = '{}'
        context['LOGINZA_IFRAME_URL'] = quote(settings.URL_PREFIX+reverse('loginza.views.return_callback'), '')

    return context

def grakon_media(request):
    media = Media()
    media.add_css({
        'all': (
            'libs/yaml/base.css',
            'css/hlist.css',
            'libs/jquery-ui/jquery-ui.css',
            'css/layout.css',
            'css/typography.css',
            'css/style.css',
            'libs/tipsy/tipsy.css',
            'css/julia_style.css',
        ),
    })

    if settings.DEBUG:
        js = ('libs/jquery.js', 'libs/jquery-ui/jquery-ui.js')
    else:
        js = ('https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js',
                'https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js')

    js += (
        'libs/underscore.js',
        'libs/tipsy/jquery.tipsy.js',
        'libs/backbone.js',
        #'http://userapi.com/js/api/openapi.js?47', # for VKontakte comments
        'http://loginza.ru/js/widget.js',
        'js/main.js',
    )
    media.add_js(js)
    return {'grakon_media': media}

def uni_form_media(request):
    media = Media()
    media.add_css({
        'all': (
            'libs/uni-form/uni-form.css',
            'libs/uni-form/default.uni-form.css'
        )
    })
    media.add_js((
        'libs/uni-form/uni-form.jquery.js',
    ))
    return {'uni_form_media': media}
