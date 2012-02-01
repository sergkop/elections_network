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

    if not location.parent_2:
        query |= Q(location__parent_2=location) if location.parent_1 else Q(location__parent_1=location)

    for role in Role.objects.filter(query).select_related():
        participants.setdefault(role.type, []).append(role.user)

    # Get sub-regions
    if location.parent_2:
        sub_regions = []
    elif location.parent_1:
        sub_regions = list(Location.objects.filter(parent_2=location))
    else:
        sub_regions = list(Location.objects.filter(parent_1=location, parent_2=None))

    context = {
        'current_location': location,
        'participants': participants,
        'links': list(Link.objects.filter(location=location)),
        'locations': list(Location.objects.filter(parent_1=None).order_by('name')),
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

        if location.parent_2: # 3rd level location
            return HttpResponse('[]') # 3rd level locations have no children
        elif location.parent_1: # 2nd level location
            res = []
            for loc in Location.objects.filter(parent_2=location).order_by('name'):
                res.append({'name': loc.name, 'id': loc.id})
            return HttpResponse(json.dumps(res))
        else: # 1st level location
            res = []
            for loc in Location.objects.filter(parent_1=location, parent_2=None).order_by('name'):
                res.append({'name': loc.name, 'id': loc.id})
            return HttpResponse(json.dumps(res))

    return HttpResponse('[]')
