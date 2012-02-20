# coding=utf8
from .forms import MessageForm, FeedbackForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import View
from django.views.generic.edit import FormView
from grakon.models import Profile
from grakon.utils import ajaxize
from locations.models import Location
from organizations.models import Organization
from smtplib import SMTPException
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
        self.data = ''
        try:
            self.organization = Organization.objects.get(signup_observers=True,
                    name=self.request.POST.get('organization', ''))
        except Organization.DoesNotExist:
            if self.request.POST.get('data'):
                self.data = self.request.POST.get('data', '')[:50]
            else:
                return u'Организация указана неверно'

    def role_fields(self):
        return {'organization': getattr(self, 'organization', None), 'data': getattr(self, 'data', '')}

class BaseRoleWithDataSignupView(RoleSignupView):
    def get_data(self):
        self.data = self.request.POST.get('data', '')[:50]
        if not self.data:
            return u'Необходимо ввести вашу организацию'

    def role_fields(self):
        return {'data': self.data}

class JournalistSignupView(BaseRoleWithDataSignupView):
    role = 'journalist'

    def get_data(self):
        try:
            self.organization = Organization.objects.get(signup_journalists=True,
                    name=self.request.POST.get('organization', ''))
        except Organization.DoesNotExist:
            if self.request.POST.get('data'):
                self.data = self.request.POST.get('data', '')[:50]
            else:
                return u'Организация указана неверно'

    def role_fields(self):
        return {'organization': getattr(self, 'organization', None), 'data': getattr(self, 'data', '')}

class LawyerSignupView(BaseRoleWithDataSignupView):
    role = 'lawyer'

    def get_data(self):
        self.data = ''
        try:
            self.organization = Organization.objects.get(signup_lawyers=True,
                    name=self.request.POST.get('organization', ''))
        except Organization.DoesNotExist:
            if self.request.POST.get('data'):
                self.data = self.request.POST.get('data', '')[:50]
            else:
                return u'Организация указана неверно'

    def role_fields(self):
        return {'organization': getattr(self, 'organization', None), 'data': getattr(self, 'data', '')}

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

class SendMessage(FormView):
    form_class = MessageForm
    
    def get_form_kwargs(self):
        kwargs = super(SendMessage, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs
    
    def form_valid(self, form):
        result = form.send()
        if result:
            return result
        return ajaxize(form)
        
    def form_invalid(self, form):
        return ajaxize(form)

#def send_message(request):
#    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
#        try:
#            profile = Profile.objects.get(username=request.POST.get('username', ''))
#        except Profile.DoesNotExist:
#            return HttpResponse(u'Пользователь не существует')
#
#        title = request.POST.get('message_title', '')
#        if title == '':
#            return HttpResponse(u'Введите тему сообщения')
#
#        message_body = request.POST.get('message_body', '')
#        if message_body == '':
#            return HttpResponse(u'Введите текст сообщения')
#
#        try:
#            send_mail(title, message_body, request.user.email, [profile.user.email], fail_silently=False)
#        except SMTPException:
#            return HttpResponse(u'Не удалось отправить сообщение')
#
#        return HttpResponse('ok')
#
#    return HttpResponse(u'Ошибка')

send_message = login_required(SendMessage.as_view())

class Feedback(FormView):
    form_class = FeedbackForm
    template_name = 'static_pages/how_to_help/base.html'
    
    def get_context_data(self, **kwargs):
        ctx = super(Feedback, self).get_context_data(**kwargs)
        ctx.update({
            'tab': 'feedback'
        })
        return ctx

    def get_form_kwargs(self):
        kwargs = super(Feedback, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs
    
    def form_valid(self, form):
        form.send()
        return redirect('feedback_thanks')
        
feedback = Feedback.as_view()
