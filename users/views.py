# coding=utf8
from smtplib import SMTPException

from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import HttpResponse
from django.views.generic.base import View

from grakon.models import Profile
from locations.models import Location
from organizations.models import Organization
from users.models import Contact, Role

class RoleSignupView(View):
    role = '' # 'voter', 'observer'

    def get_data(self):
        """
        Method to extract role-specific data.
        Return error or None.
        """
        return None

    def role_fields(self):
        return {}

    def post(self, request):
        error = u'Вы можете записаться только на уровне ТИК или УИК'

        if not (request.is_ajax() and request.user.is_authenticated()):
            return HttpResponse(error)

        try:
            location_id = int(self.request.POST.get('uik', self.request.POST.get('tik', '')))
        except ValueError:
            return HttpResponse(error)

        try:
            self.location = Location.objects.exclude(region=None).get(id=location_id)
        except Location.DoesNotExist:
            return HttpResponse(error)

        res = self.get_data()
        if res: # return error
            return HttpResponse(res)

        defaults = self.role_fields()
        defaults['location'] = self.location

        try:
            role, created = Role.objects.get_or_create(type=self.role,
                    user=request.user.get_profile(), defaults=defaults)
        except IntegrityError:
            return HttpResponse(u'Ошибка базы данных')

        if not created:
            for field in defaults:
                setattr(role, field, defaults[field])
            role.save()

        return HttpResponse('ok')

class VoterSignupView(RoleSignupView):
    role = 'voter'

class ObserverSignupView(RoleSignupView):
    role = 'observer'

    def get_data(self):
        try:
            self.organization = Organization.objects.get(
                    name=self.request.POST.get('organization', ''))
        except Organization.DoesNotExist:
            return u'Организация указана неверно'

    def role_fields(self):
        return {'organization': self.organization}

class BaseRoleWithDataSignupView(RoleSignupView):
    def get_data(self):
        self.data = self.request.POST.get('data', '')[:50]
        if not self.data:
            return u'Необходимо ввести вашу организацию'

    def role_fields(self):
        return {'data': self.data}

class JournalistSignupView(BaseRoleWithDataSignupView):
    role = 'journalist'

class LawyerSignupView(BaseRoleWithDataSignupView):
    role = 'lawyer'

class ProsecutorSignupView(BaseRoleWithDataSignupView):
    role = 'prosecutor'

class MemberSignupView(RoleSignupView):
    role = 'member'

def add_to_contacts(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        try:
            contact = Profile.objects.get(username=request.POST.get('username', ''))
        except Profile.DoesNotExist:
            return HttpResponse(u'Пользователь не существует')

        try:
            Contact.objects.create(user=request.user.get_profile(), contact=contact)
        except IntegrityError:
            return HttpResponse(u'Пользователь уже добавлен в контакты')

        return HttpResponse('ok')

    return HttpResponse(u'Ошибка')

def remove_from_contacts(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        try:
            contact = Profile.objects.get(username=request.POST.get('username', ''))
        except Profile.DoesNotExist:
            return HttpResponse(u'Пользователь не существует')

        Contact.objects.filter(user=request.user.get_profile(), contact=contact).delete()
        return HttpResponse('ok')

    return HttpResponse(u'Ошибка')

def send_message(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        try:
            profile = Profile.objects.get(username=request.POST.get('username', ''))
        except Profile.DoesNotExist:
            return HttpResponse(u'Пользователь не существует')

        title = request.POST.get('message_title', '')
        if title == '':
            return HttpResponse(u'Введите тему сообщения')

        message_body = request.POST.get('message_body', '')
        if message_body == '':
            return HttpResponse(u'Введите текст сообщения')

        try:
            send_mail(title, message_body, request.user.email, [profile.user.email], fail_silently=False)
        except SMTPException:
            return HttpResponse(u'Не удалось отправить сообщение')

        return HttpResponse('ok')

    return HttpResponse(u'Ошибка')
