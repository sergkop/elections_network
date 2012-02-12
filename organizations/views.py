# -*- coding:utf-8 -*-
from django.http import Http404
from django.views.generic.base import TemplateView

from locations.models import Location
from organizations.models import Organization, OrganizationCoverage

class BaseOrganizationView(object):
    template_name = 'organizations/base.html'

    def get_context_data(self, **kwargs):
        ctx = super(BaseOrganizationView, self).get_context_data(**kwargs)

        try:
            organization = Organization.objects.select_related().get(name=kwargs['name'])
        except Organization.DoesNotExist:
            raise Http404(u'Организация не найдена')

        location_ids = OrganizationCoverage.objects.filter(organization=organization).values_list('location_id', flat=True)
        locations = list(Location.objects.filter(id__in=location_ids).select_related())
        if None in location_ids:
            locations.append(None) # special processing for the whole country

        ctx.update({
            'name': kwargs['name'],
            'view': kwargs['view'],
            'organization': organization,
            'locations': locations,
        })
        return ctx


class OrganizationView(BaseOrganizationView, TemplateView):
    pass

organization_view = OrganizationView.as_view()


