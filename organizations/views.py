# -*- coding:utf-8 -*-
from .forms import CreateOrganizationForm, EditOrganizationForm, \
    VerificationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from grakon.models import Profile
from locations.models import Location
from organizations.models import Organization, OrganizationCoverage, \
    OrganizationRepresentative
from users.models import Role


class BaseOrganizationView(object):
    template_name = 'organizations/base.html'
    view = None # 'organization_info', 'organization_edit' or 'organization_create'
    model = Organization

    def get_object(self, queryset=None):
        return get_object_or_404(Organization.objects.select_related(), name=self.kwargs.get('name', ''))

    def get_context_data(self, **kwargs):
        ctx = super(BaseOrganizationView, self).get_context_data(**kwargs)
        is_representative = False
        if self.request.user.is_authenticated():
            try:
                profile = self.request.user.profile
                is_representative = profile.is_representative(self.object)
            except ObjectDoesNotExist:
                pass 
            
        locations = self.object.get_locations()

        ctx.update({
            'name': self.kwargs['name'],
            'view': self.view,
            'organization': self.object,
            'locations': locations,
            'representatives': self.object.get_representative_profiles(),
            'observers': self.object.get_observers(),
            'is_representative': is_representative,
        })
        return ctx

class OrganizationInfoView(BaseOrganizationView, DetailView):
    view = 'organization_info'

organization_info = OrganizationInfoView.as_view()

class EditOrganizationView(BaseOrganizationView, UpdateView):
    form_class = EditOrganizationForm
    view = 'edit_organization'

@login_required
def edit_organization(request, name):
    # TODO: only representatives can edit (do redirect)
    return EditOrganizationView.as_view()(request, name=name)

class CreateOrganizationView(CreateView):
    template_name = 'organizations/create.html'
    form_class = CreateOrganizationForm
    model = Organization

    def form_valid(self, form):
        response = super(CreateOrganizationView, self).form_valid(form)

        profile = self.request.user.get_profile()
        organization = self.object

        OrganizationRepresentative.objects.get_or_create(organization=organization,
                user=self.request.user.get_profile())

        OrganizationCoverage.objects.get_or_create(organization=organization, location=form.location)

        # Send email to us stating that new organization has registered
        subject = u'Зарегистрирована новая организация - %s' % organization.title

        message = u"""Зарегистрирована новая организация:
Название: %s
Страница: %s
Сайт: %s
Пользователь: %s
Email: %s
""" % (organization.title, organization.get_absolute_url(), organization.website, profile.username, profile.user.email)

        send_mail(subject, message, 'admin@grakon.org', ['admin@grakon.org'], fail_silently=False)

        return response

create_organization = login_required(CreateOrganizationView.as_view())

class Verification(BaseOrganizationView, DetailView):
    view = 'verification'
    
    def get_context_data(self, **kwargs):
        ctx = super(Verification, self).get_context_data(**kwargs)
        roles = self.object.get_unverified_roles()
        for role in roles:
            role.form = VerificationForm(request=self.request, instance=role, initial={'verified': True})
        ctx.update({
            'tab': 'verification',
            'roles': roles
        })
        return ctx
    
verification = login_required(Verification.as_view())

class Verify(UpdateView):
    model = Role
    form_class = VerificationForm
    
    def get_form_kwargs(self):
        kwargs = super(Verify, self).get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs
    
    def form_valid(self, form):
        self.object = form.save()
        return HttpResponse('ok')
    
    def form_invalid(self, form):
        return HttpResponse(u'Подтвердить пользователя не удалось')
    
verify = login_required(Verify.as_view())