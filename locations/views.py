# coding=utf8
import json

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.views.generic.base import TemplateView

from grakon.utils import authenticated_redirect
from locations.models import Location
from locations.utils import regions_list
from organizations.models import OrganizationCoverage
from links.models import Link
from users.models import Role

# TODO: mark links previously reported by user
class LocationView(TemplateView):
    template_name = 'locations/base.html'

    def get_context_data(self, **kwargs):
        ctx = super(LocationView, self).get_context_data(**kwargs)

        loc_id = int(kwargs['loc_id'])
        try:
            location = Location.objects.select_related().get(id=loc_id)
        except Location.DoesNotExist:
            raise Http404(u'Избирательный округ не найден')

        # Get the list of role
        participants = {} # {role_type: [users]}
        query = Q(location=location)

        if not location.tik:
            query |= Q(location__tik=location) if location.region else Q(location__region=location)

        for role in Role.objects.filter(query).select_related():
            participants.setdefault(role.type, []).append(role.user)

        # Get sub-regions
        sub_regions = []
        voter_count = 0
        if location.region is None:
            for loc in Location.objects.filter(region=location, tik=None).order_by('name'):
                sub_regions.append((loc.id, loc.name))

            voter_count = Role.objects.filter(type='voter', location__region=location).count()
        elif location.tik is None:
            for loc in Location.objects.filter(tik=location).order_by('name'):
                sub_regions.append((loc.id, loc.name))

            voter_count = Role.objects.filter(type='voter', location__tik=location).count()

        ctx.update({
            'loc_id': kwargs['loc_id'],
            'view': kwargs['view'],
            'current_location': location,
            'participants': participants,
            'links': list(Link.objects.filter(location=location)),
            'locations': regions_list(),
            'is_voter_here': self.request.user.is_authenticated() and any(self.request.user==voter.user for voter in participants.get('voter', [])),
            'sub_regions': sub_regions,

            'voter_count': voter_count,
            'organizations': OrganizationCoverage.objects.organizations_at_location(location),
        })
        return ctx

location_view = LocationView.as_view()

def location_register(request, **kwargs):
    if request.user.is_authenticated():
        return redirect(reverse('location_info', args=[kwargs['loc_id']]))
    return location_view(request, **kwargs)

def get_sub_regions(request):
    if request.is_ajax():
        try:
            location_id = int(request.GET.get('location', ''))
        except ValueError:
            return HttpResponse('[]')

        try:
            location = Location.objects.select_related().get(id=location_id)
        except Location.DoesNotExist:
            return HttpResponse('[]')

        if location.tik: # 3rd level location
            return HttpResponse('[]') # 3rd level locations have no children
        elif location.region: # 2nd level location
            res = []
            for loc in Location.objects.filter(tik=location).order_by('name'):
                res.append({'name': loc.name, 'id': loc.id})
            return HttpResponse(json.dumps(res))
        else: # 1st level location
            res = []
            for loc in Location.objects.filter(region=location, tik=None).order_by('name'):
                res.append({'name': loc.name, 'id': loc.id})
            return HttpResponse(json.dumps(res))

    return HttpResponse('[]')

# TODO: restructure it and take only one parameter
def goto_location(request):
    tab = request.GET.get('tab', '')
    dialog = request.GET.get('dialog', '')
    for name in ('uik', 'tik', 'region'):
        try:
            location_id = int(request.GET.get(name, ''))
        except ValueError:
            continue

        url = reverse('location_info', args=[location_id])
        if tab:
            url += '/' + tab
        if dialog:
            url += '?dialog=' + dialog
        return HttpResponseRedirect(url)

    return HttpResponseRedirect(reverse('main'))

# TODO: needs to be cached
def map_data(request):
    context = {
        'all_locations': list(Location.objects.all()),
    }
    return render_to_response('locations/map_data.js', context, mimetype='application/javascript')
