import json

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from geography.models import LocationModel
from links.models import LinkModel
from users.models import ParticipationModel

def goto_location(request):
    try:
        location_id = int(request.GET.get('region_3'))
    except ValueError:
        try:
            location_id = int(request.GET.get('region_2'))
        except ValueError:
            try:
                location_id = int(request.GET.get('region_1'))
            except ValueError:
                return HttpResponseRedirect(reverse('main'))
            else:
                return HttpResponseRedirect(reverse('location', args=[location_id]))
        else:
            return HttpResponseRedirect(reverse('location', args=[location_id]))
    else:
        return HttpResponseRedirect(reverse('location', args=[location_id]))

# TODO: mark links previously reported by user
def location(request, loc_id):
    try:
        id = int(loc_id)
    except ValueError:
        raise Http404

    try:
        location = LocationModel.objects.select_related().get(id=id)
    except LocationModel.DoesNotExist:
        raise Http404

    participants = {} # {participation_type: [users]}

    query = Q(location=location)
    if not location.parent_2:
        query |= Q(location__parent_2=location) if location.parent_1 else Q(location__parent_1=location)

    for participation in ParticipationModel.objects.filter(query).select_related():
        participants.setdefault(participation.type, []).append(participation.user)

    context = {
        'current_location': location,
        'participants': participants,
        'links': list(LinkModel.objects.filter(location=location)),
        'locations': list(LocationModel.objects.filter(parent_1=None).order_by('name')),
        'is_voter_here': request.user.is_authenticated() and any(request.user==voter for voter in participants.get('voter', [])),
    }
    return render_to_response('location.html', context_instance=RequestContext(request, context))

def get_sub_regions(request):
    if request.is_ajax():
        try:
            location_id = int(request.GET.get('location', ''))
        except ValueError:
            return HttpResponse('[]')

        try:
            location = LocationModel.objects.select_related().get(id=location_id)
        except LocationModel.DoesNotExist:
            return HttpResponse('[]')

        if location.parent_2: # 3rd level location
            return HttpResponse('[]') # 3rd level locations have no children
        elif location.parent_1: # 2nd level location
            res = []
            for loc in LocationModel.objects.filter(parent_2=location).order_by('name'):
                res.append({'name': loc.name, 'id': loc.id})
            return HttpResponse(json.dumps(res))
        else: # 1st level location
            res = []
            for loc in LocationModel.objects.filter(parent_1=location, parent_2=None).order_by('name'):
                res.append({'name': loc.name, 'id': loc.id})
            return HttpResponse(json.dumps(res))

    return HttpResponse('[]')
