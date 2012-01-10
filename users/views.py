from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from users.models import ParticipationModel

def current_profile(request):
    """ Show profile of the currently logged in user """
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    context = {
        'user': request.user,
        'participations': list(ParticipationModel.objects.filter(user=request.user).select_related()),
    }
    return render_to_response('profile.html', context_instance=RequestContext(request, context))

def profile(request, username):
    if request.user.username == username:
        return current_profile(request)

    user = get_object_or_404(User, username=username)

    context = {
        'user': user,
        'participations': list(ParticipationModel.objects.filter(user=user).select_related()),
    }
    return render_to_response('profile.html', context_instance=RequestContext(request, context))
