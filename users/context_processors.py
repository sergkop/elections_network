import json
from urllib import quote

from django.conf import settings
from django.core.urlresolvers import reverse

from links.models import Link, LINK_REPORT_CHOICES
from users.models import Contact, ReportUser, USER_REPORT_CHOICES

def user_data(request):
    context = {
        'LINK_REPORT_CHOICES': LINK_REPORT_CHOICES,
        'USER_REPORT_CHOICES': USER_REPORT_CHOICES,
    }
    if request.user.is_authenticated():
        context['CONTACTS'] = json.dumps(
                list(Contact.objects.filter(user=request.user).values_list('contact__username', flat=True)))
        context['REPORTED_USERS'] = json.dumps(
                list(ReportUser.objects.filter(reporter=request.user).values_list('user__username', flat=True)))
    else:
        if request.path is not None and request.path not in settings.LOGINZA_AMNESIA_PATHS:
            request.session['loginza_return_path'] = request.path

        context['CONTACTS'] = '[]'
        context['REPORTED_USERS'] = '[]'
        context['LOGINZA_IFRAME_URL'] = quote(settings.URL_PREFIX+reverse('loginza.views.return_callback'), '')

    return context
