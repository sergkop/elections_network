import json
from urllib import quote

from django.conf import settings
from django.core.urlresolvers import reverse

from users.models import Contact
from reports.models import Report, REPORT_REASONS

def user_data(request):
    context = {
        'REPORT_REASONS': json.dumps(REPORT_REASONS, ensure_ascii=False),
        #'VK_APP_ID': settings.VK_APP_ID,
        'YA_METRIKA_ID': settings.YA_METRIKA_ID,
        'DISQUS_SHORTNAME': settings.DISQUS_SHORTNAME,
        'YANDEX_MAPS_KEY': settings.YANDEX_MAPS_KEY,
    }
    if request.user.is_authenticated():
        context['CONTACTS'] = json.dumps(
                list(Contact.objects.filter(user=request.user).values_list('contact__username', flat=True)))
        context['REPORTS'] = json.dumps(Report.objects.user_reports(request.user))
    else:
        if request.path is not None and request.path not in settings.LOGINZA_AMNESIA_PATHS:
            request.session['loginza_return_path'] = request.path

        context['CONTACTS'] = '[]'
        context['REPORTS'] = '{}'
        context['LOGINZA_IFRAME_URL'] = quote(settings.URL_PREFIX+reverse('loginza.views.return_callback'), '')

    return context
