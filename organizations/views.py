# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

from grakon.models import Profile
from locations.models import Location
from organizations.forms import CreateOrganizationForm, EditOrganizationForm
from organizations.models import Organization, OrganizationCoverage, OrganizationRepresentative
from users.models import Role

class BaseOrganizationView(object):
    template_name = 'organizations/base.html'
    view = None # 'organization_info', 'organization_edit' or 'organization_create'
    model = Organization

    def get_object(self, queryset=None):
        return get_object_or_404(Organization.objects.select_related(),
                name=self.kwargs.get('name', ''))

    def get_representatives(self):
        if not hasattr(self, 'representatives'):
            self.representative_ids = OrganizationRepresentative.objects.filter(organization=self.object) \
                .values_list('user', flat=True)
            self.representatives = Profile.objects.filter(id__in=self.representative_ids)

    def get_context_data(self, **kwargs):
        ctx = super(BaseOrganizationView, self).get_context_data(**kwargs)

        organization = self.object

        self.get_representatives()
        is_representative = self.request.user.id in self.representative_ids

        location_ids = OrganizationCoverage.objects.filter(organization=organization).values_list('location_id', flat=True)
        locations = list(Location.objects.filter(id__in=location_ids).select_related())
        if None in location_ids:
            locations.append(None) # special processing for the whole country

        participants = Role.objects.get_participants(Q(organization=organization))
        counters = {}
        if organization.signup_observers:
            counters['observer'] = Role.objects.filter(organization=organization, type='observer').count()
        if organization.signup_journalists:
            counters['journalist'] = Role.objects.filter(organization=organization, type='journalist').count()

        ctx.update({
            'name': self.kwargs['name'],
            'view': self.view,
            'organization': organization,
            'locations': locations,
            'representatives': self.representatives,
            'participants': participants,
            'counters': counters,
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

        profile = self.request.profile
        organization = self.object

        OrganizationRepresentative.objects.get_or_create(organization=organization, user=profile)

        OrganizationCoverage.objects.get_or_create(organization=organization, location=form.location)

        # Send email to us stating that new organization has registered
        subject = u'Зарегистрирована новая организация - %s' % organization.title

        message = u'Зарегистрирована новая организация:\n' \
                u'Название: %s\n' \
                u'Страница: http://grakon.org%s\n' \
                u'Сайт: %s\n' \
                u'Пользователь: http://grakon.org/user/%s\n' \
                u'Email: %s' % (
                organization.title, organization.get_absolute_url(), organization.website,
                profile.username, profile.user.email)

        send_mail(subject, message, 'admin@grakon.org', ['admin@grakon.org'], fail_silently=False)

        return response

create_organization = login_required(CreateOrganizationView.as_view())
