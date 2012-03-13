# coding=utf8
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import loader, RequestContext
from django.views.generic.base import TemplateView

from loginza.models import UserMap

from grakon.forms import ProfileForm
from grakon.utils import cache_function
from locations.models import Location
from locations.utils import get_roles_counters, regions_list
from navigation.models import Page
from organizations.models import Organization, OrganizationCoverage
from protocols.models import Protocol
from protocols.utils import results_table_data
from users.models import CommissionMember, Role

@cache_function('main_page', 30)
def main_page_context():
    inactive_ids = UserMap.objects.filter(verified=False).values_list('user', flat=True)
    total_counter = User.objects.exclude(email='').filter(is_active=True) \
            .exclude(id__in=inactive_ids).count()

    cik_protocols_by_location = dict((p.location_id, p) for p in Protocol.objects.from_cik() \
            .filter(location__region=None))

    protocols_by_location = dict((p.location_id, p) \
            for p in Protocol.objects.verified().filter(location__region=None))

    results_protocol = Protocol(p9=0, p10=0, p19=0, p20=0, p21=0, p22=0, p23=0)
    for loc_id in cik_protocols_by_location:
        if protocols_by_location[loc_id].p10 == 0: # TODO: temporary
            p = cik_protocols_by_location[loc_id]
        else:
            p = protocols_by_location[loc_id]

        for field in ('p9', 'p10', 'p19', 'p20', 'p21', 'p22', 'p23'):
            setattr(results_protocol, field, getattr(results_protocol, field)+getattr(p, field))

    protocol_data = results_table_data([results_protocol])

    sub_regions = regions_list()
    return {
        'counters': get_roles_counters(None),
        'locations': sub_regions,
        'sub_regions': sub_regions,
        'organizations': OrganizationCoverage.objects.organizations_at_location(None),
        'total_counter': total_counter,
        'protocol_data': protocol_data,

        'disqus_identifier': 'main',
    }

class BaseMainView(TemplateView):
    template_name = 'main/base.html'
    tab = '' # 'main' or 'wall'

    def get_context_data(self, **kwargs):
        ctx = super(BaseMainView, self).get_context_data(**kwargs)

        ctx.update(main_page_context())
        ctx.update({'tab': self.tab})

        if self.request.user.is_authenticated():
            ctx.update({'form': ProfileForm()})

        return ctx

#class MainView(BaseMainView):
#    tab = 'main'
#main = MainView.as_view()

def main(request):
    if not request.user.is_authenticated():
        html = cache.get('main_html')
        if html:
            return HttpResponse(html)

    ctx = {'tab': 'main'}
    ctx.update(main_page_context())
    if request.user.is_authenticated():
        ctx.update({'form': ProfileForm()})

    html = loader.render_to_string('main/base.html', context_instance=RequestContext(request, ctx))

    if not request.user.is_authenticated():
        cache.set('main_html', html, 300)

    return HttpResponse(html)

class WallView(BaseMainView):
    tab = 'wall'
wall = WallView.as_view()

class MainNewsView(BaseMainView):
    tab = 'main_news'
main_news = MainNewsView.as_view()

class MainInfoView(BaseMainView):
    tab = 'main_info'
main_info = MainInfoView.as_view()

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
