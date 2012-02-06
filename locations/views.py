import json

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from locations.models import Location
from links.models import Link
from users.models import Role

# TODO: restructure it and take only one parameter
def goto_location(request):
    for name in ('region_3', 'region_2', 'region_1'):
        try:
            location_id = int(request.GET.get(name, ''))
        except ValueError:
            continue

        return HttpResponseRedirect(reverse('location', args=[location_id]))

    return HttpResponseRedirect(reverse('main'))

# TODO: mark links previously reported by user
def location(request, loc_id):
    try:
        id = int(loc_id)
    except ValueError:
        raise Http404

    try:
        location = Location.objects.select_related().get(id=id)
    except Location.DoesNotExist:
        raise Http404

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
        sub_regions = list(Location.objects.filter(tik=location))
    else:
        sub_regions = list(Location.objects.filter(region=location, tik=None))

    context = {
        'current_location': location,
        'participants': participants,
        'links': list(Link.objects.filter(location=location)),
        'locations': list(Location.objects.filter(region=None).order_by('name')),
        'is_voter_here': request.user.is_authenticated() and any(request.user==voter for voter in participants.get('voter', [])),
        'sub_regions': sub_regions,
    }
    return render_to_response('location.html', context_instance=RequestContext(request, context))

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
