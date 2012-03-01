# coding=utf8
from smtplib import SMTPException

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
from users.forms import CommissionMemberForm, FeedbackForm, MessageForm, WebObserverForm
from users.models import Contact, Role, WebObserver

class RoleSignupView(View):
    role = '' # 'voter', 'observer'
    levels = [] # list of 'region', 'tik', 'uik'

    def get_data(self):
        """
        Method to extract role-specific data.
        Return error or None.
        """
        return None

    def role_fields(self):
        return {}

    def post(self, request):
        if not (request.is_ajax() and request.user.is_authenticated()):
            return HttpResponse(u'Вам необходимо войти в систему')

        post_data = self.request.POST

        try:
            location_id = int(post_data.get('uik', post_data.get('tik', post_data.get('region', ''))))
        except ValueError:
            return HttpResponse(u'Неверно указан избирательный округ')

        try:
            self.location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            return HttpResponse(u'Неверно указан избирательный округ')

        if self.location.is_region() and 'region' not in self.levels:
            return HttpResponse(u'Вы не можете записаться на уровне субъекта федерации')

        if self.location.is_tik() and 'tik' not in self.levels:
            return HttpResponse(u'Необходимо выбрать избирательный участок')

        if self.location.is_uik() and 'uik' not in self.levels:
            return HttpResponse(u'Вы не можете записаться на уровне избирательного участка')

        res = self.get_data()
        if res: # return error
            return HttpResponse(res)

        defaults = self.role_fields()
        defaults['location'] = self.location

        try:
            role, created = Role.objects.get_or_create(type=self.role,
                    user=request.profile, defaults=defaults)
        except IntegrityError:
            return HttpResponse(u'Ошибка базы данных')

        if not created:
            for field in defaults:
                setattr(role, field, defaults[field])
            role.save()

        return HttpResponse('ok')

class VoterSignupView(RoleSignupView):
    role = 'voter'
    levels = ['tik', 'uik']

class ObserverSignupView(RoleSignupView):
    role = 'observer'
    levels = ['tik', 'uik']

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
    levels = ['tik', 'uik']

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
    levels = ['region', 'tik', 'uik']

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
    levels = ['region', 'tik', 'uik']

class MemberSignupView(RoleSignupView):
    role = 'member'
    levels = ['region', 'tik', 'uik']

class SupporterSignupView(RoleSignupView):
    role = 'supporter'
    levels = ['uik']

def add_to_contacts(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        try:
            contact = Profile.objects.get(username=request.POST.get('username', ''))
        except Profile.DoesNotExist:
            return HttpResponse(u'Пользователь не существует')

        try:
            Contact.objects.create(user=request.profile, contact=contact)
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

        Contact.objects.filter(user=request.profile, contact=contact).delete()
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

def add_commission_member(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        try:
            location_id = int(request.POST.get('location'))
        except ValueError:
            return HttpResponse(u'Неверно указан избирательный округ')

        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            return HttpResponse(u'Неверно указан избирательный округ')

        form = CommissionMemberForm(request.POST)
        if form.is_valid():
            commission_member = form.save(commit=False)
            commission_member.location = location
            commission_member.user = request.profile
            commission_member.save()
            return HttpResponse('ok')
        else:
            return HttpResponse(u'Заполните обязательные поля')

    return HttpResponse(u'Ошибка')

def become_web_observer(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        try:
            location_id = int(request.POST.get('location'))
        except ValueError:
            return HttpResponse(u'Неверно указан избирательный округ')

        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            return HttpResponse(u'Неверно указан избирательный округ')

        form = WebObserverForm(request.POST)
        if form.is_valid():
            if not form.cleaned_data['start_time'] in range(7, 24):
                return HttpResponse(u'Время начала наблюдения указано неверно')

            if not form.cleaned_data['end_time'] in range(8, 25):
                return HttpResponse(u'Время окончания наблюдения указано неверно')

            if form.cleaned_data['end_time'] <= form.cleaned_data['start_time']:
                return HttpResponse(u'Время окончания наблюдения должно быть позднее начала')

            form_web_observer = form.save(commit=False)
            form_web_observer.location = location
            form_web_observer.user = request.profile
            form_web_observer.save()

            # Merge overlapping web observers
            web_observers = WebObserver.objects.filter(location=location, user=request.profile)

            times_covered = set()
            for web_observer in web_observers:
                for time in range(web_observer.start_time, web_observer.end_time):
                    times_covered.add(time)

            WebObserver.objects.filter(location=location, user=request.profile).delete()
            for time in times_covered:
                WebObserver.objects.create(location=location, user=request.profile,
                        start_time=time, end_time=time+1, capture_video=form_web_observer.capture_video,
                        url=form_web_observer.url)

            return HttpResponse('ok')
        else:
            return HttpResponse(u'Поля заполнены неверно')

    return HttpResponse(u'Ошибка')
