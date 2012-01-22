import json
from urllib import quote

from django.conf import settings
from django.core.urlresolvers import reverse

from users.models import Contact

def user_data(request):
    if request.user.is_authenticated():
        return {
            'CONTACTS': json.dumps(list(Contact.objects.filter(user=request.user).values_list('contact__username', flat=True))),
        }
    else:
        if request.path is not None and request.path not in settings.LOGINZA_AMNESIA_PATHS:
            request.session['loginza_return_path'] = request.path

        return {
            'CONTACTS': '[]',
            'LOGINZA_IFRAME_URL': quote(settings.URL_PREFIX+reverse('loginza.views.return_callback'), '')
        }
