#from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
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

    location = get_object_or_404(LocationModel, id=id)

    participants = {} # {participation_type: [users]}
    for participation in ParticipationModel.objects.filter(location=location).select_related():
        participants.setdefault(participation.type, []).append(participation.user)

    context = {
        'current_location': location,
        'participants': participants,
        'links': list(LinkModel.objects.filter(location=location)),
        'locations': list(LocationModel.objects.filter(parent_1=None)),
        'is_voter_here': request.user.is_authenticated() and any(request.user==voter for voter in participants.get('voter', [])),
    }
    return render_to_response('location.html', context_instance=RequestContext(request, context))
