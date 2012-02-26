# coding=utf8
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic.base import TemplateView

from grakon.forms import ProfileForm
from grakon.utils import cache_view
from locations.models import Location
from locations.utils import get_roles_counters, regions_list
from navigation.models import Page
from organizations.models import Organization, OrganizationCoverage
from users.models import Role

class MainView(TemplateView):
    template_name = 'main/base.html'

    def get_context_data(self, **kwargs):
        ctx = super(MainView, self).get_context_data(**kwargs)

        sub_regions = regions_list()
        ctx.update({
            'tab': kwargs['tab'],
            'counters': get_roles_counters(None),
            'locations': sub_regions,
            'sub_regions': sub_regions,
            'organizations': OrganizationCoverage.objects.organizations_at_location(None),
            'total_counter': User.objects.exclude(email='').filter(is_active=True).count(),

            'disqus_identifier': 'main',
        })

        if self.request.user.is_authenticated():
            ctx.update({'form': ProfileForm()})

        return ctx

main = MainView.as_view()
#main = cache_view('main_page', 60)(MainView.as_view())
wall = MainView.as_view()

def static_page(request, name, template):
    context = {
        'tab': name,
        'template': template,
    }
    return render_to_response(template, context_instance=RequestContext(request, context))

def sitemap(request):
    context = {
        'locations': Location.objects.filter(region=None).only('id', 'name'),
        'organizations': Organization.objects.filter(verified=True),
    }
    return render_to_response('sitemap.html', context_instance=RequestContext(request, context))
