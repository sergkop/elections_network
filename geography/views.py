import json

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from geography.models import LocationModel
from links.models import LinkModel
from users.models import ParticipationModel

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
    for participation in ParticipationModel.objects.filter(location=location).select_related():
        participants.setdefault(participation.type, []).append(participation.user)

    context = {
        'current_location': location,
        'participants': participants,
        'links': list(LinkModel.objects.filter(location=location)),
        #'locations': list(LocationModel.objects.filter(parent_1=None).order_by('name')),
        'is_voter_here': request.user.is_authenticated() and any(request.user==voter for voter in participants.get('voter', [])),
    }
    return render_to_response('location.html', context_instance=RequestContext(request, context))

def get_sub_regions(request):
    if request.is_ajax():
        try:
            location_id = int(request.GET.get('location', ''))
        except ValueError:
            return HttpResponse('null')

        try:
            location = LocationModel.objects.select_related().get(id=location_id)
        except LocationModel.DoesNotExist:
            return HttpResponse('null')

        if location.parent_2: # 3rd level location
            return HttpResponse('null') # 3rd level locations have no children
        elif location.parent_1: # 2nd level location
            #for location in LocationModel.objects.filter(parent_2=location).order_by('name')
            return 
        else: # 1st level location
            pass

    return HttpResponse('null')
