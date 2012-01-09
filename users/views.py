from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

def profile(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    context = {}
    return render_to_response('profile.html', context_instance=RequestContext(request, context))

def login(request):
    return render_to_response()
