from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms.widgets import Media
from django.utils.safestring import mark_safe
from reports.models import Report, REPORT_REASONS
from urllib import quote
from users.models import Contact
import base64
import hashlib
import hmac
import json
import time



def get_disqus_config(user):
    template = '''
    var disqus_config = function() {
        this.page.remote_auth_s3 = "%(message)s %(sig)s %(timestamp)s";
        this.page.api_key = "%(pub_key)s";
    }
    '''
    if not user.is_authenticated():
        return ''
    secret_key = getattr(settings, 'DISQUS_SECRET_KEY', None)
    public_key = getattr(settings, 'DISQUS_PUBLIC_KEY', None)
    if secret_key is None or public_key is None:
        return ''
    profile = None
    try:
        profile = user.profile
    except:
        return ''
    
    data = json.dumps({
        'id': profile.pk,
        'username': profile.username,
        'email': profile.user.email,
    })
    message = base64.b64encode(data)
    timestamp = int(time.time())
    sig = hmac.HMAC(secret_key, '%s %s' % (message, timestamp), hashlib.sha1).hexdigest()
    config = template % {'message': message,
                         'sig': sig,
                         'timestamp': timestamp,
                         'pub_key': public_key}
    return mark_safe(config)


def user_data(request):
    context = {
        'REPORT_REASONS': json.dumps(REPORT_REASONS, ensure_ascii=False),
        'VK_APP_ID': settings.VK_APP_ID,
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
        'YA_METRIKA_ID': settings.YA_METRIKA_ID,
        'DISQUS_SHORTNAME': settings.DISQUS_SHORTNAME,
        'DISQUS_CONFIG': get_disqus_config(request.user),
        'YANDEX_MAPS_KEY': settings.YANDEX_MAPS_KEY,
        'URL_PREFIX': settings.URL_PREFIX,
    }
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        context['my_profile'] = profile
        context['CONTACTS'] = json.dumps(list(profile.contacts.values_list('contact__username', flat=True)))
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
        'http://userapi.com/js/api/openapi.js?47', # VKontakte
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
