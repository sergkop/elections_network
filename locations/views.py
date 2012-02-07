# coding=utf8
import json

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView

from locations.models import Location
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
        if location.tik:
            sub_regions = []
        elif location.region:
            sub_regions = list(Location.objects.filter(tik=location).order_by('name'))
        else:
            sub_regions = list(Location.objects.filter(region=location, tik=None).order_by('name'))

        ctx.update({
            'loc_id': kwargs['loc_id'],
            'view': kwargs['view'],
            'current_location': location,
            'participants': participants,
            'links': list(Link.objects.filter(location=location)),
            'locations': list(Location.objects.filter(region=None).order_by('name')), # used in become voter dialog
            'all_locations': list(Location.objects.all()), # needed for the map
            'is_voter_here': self.request.user.is_authenticated() and any(self.request.user==voter.user for voter in participants.get('voter', [])),
            'sub_regions': sub_regions,
        })
        return ctx

location = LocationView.as_view()

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
    for name in ('region_3', 'region_2', 'region_1'):
        try:
            location_id = int(request.GET.get(name, ''))
        except ValueError:
            continue

        return HttpResponseRedirect(reverse('location_help', args=[location_id]))

    return HttpResponseRedirect(reverse('main'))
