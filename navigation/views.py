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
from users.models import CommissionMember, Role

@cache_function('main_page', 180)
def main_page_context():
    inactive_ids = UserMap.objects.filter(verified=False).values_list('user', flat=True)
    total_counter = User.objects.exclude(email='').filter(is_active=True) \
            .exclude(id__in=inactive_ids).count()

    sub_regions = regions_list()
    return {
        'counters': get_roles_counters(None),
        'locations': sub_regions,
        'sub_regions': sub_regions,
        'organizations': OrganizationCoverage.objects.organizations_at_location(None),
        'total_counter': total_counter,

        'commission_members_count': CommissionMember.objects.count(),
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
        cache.set('main_html', html, 180)

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
