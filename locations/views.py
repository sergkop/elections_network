# coding=utf8
import json

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.views.generic.base import TemplateView

from grakon.utils import authenticated_redirect
from locations.models import Boundary, Location
from locations.utils import get_locations_data, get_roles_counters, get_roles_query, regions_list
from organizations.models import OrganizationCoverage
from links.models import Link
from organizations.models import Organization
from protocols.models import Protocol
from protocols.utils import results_table_data
from users.forms import CommissionMemberForm, WebObserverForm
from users.models import CommissionMember, Role, ROLE_CHOICES, ROLE_TYPES, WebObserver
from violations.models import Violation

# TODO: web_observers tab is not activated for tiks and lead to crush
class BaseLocationView(TemplateView):
    template_name = 'locations/base.html'

    def update_context(self):
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(BaseLocationView, self).get_context_data(**kwargs)

        loc_id = int(kwargs['loc_id'])
        try:
            self.location = location = Location.objects.select_related().get(id=loc_id)
        except Location.DoesNotExist:
            raise Http404(u'Избирательный округ не найден')

        # TODO: different query generators might be needed for different data types
        self.location_query = get_roles_query(location)

        dialog = self.request.GET.get('dialog', '')
        if not dialog in ROLE_TYPES and not dialog in ('web_observer',):
            dialog = ''

        signed_up_in_uik = False
        if self.request.user.is_authenticated():
            voter_roles = Role.objects.filter(user=self.request.profile, type='voter').select_related('location')
            if voter_roles:
                signed_up_in_uik = voter_roles[0].location.is_uik()

        counters = get_roles_counters(location)

        verified_protocols = list(Protocol.objects.verified().filter(location=location))

        try:
            cik_protocols = [Protocol.objects.from_cik().get(location=location)]
        except Protocol.DoesNotExist:
            cik_protocols = []

        cik_data = results_table_data(cik_protocols)
        protocol_data = results_table_data(verified_protocols)

        ctx.update({
            'loc_id': kwargs['loc_id'],
            'view': kwargs['view'],
            'current_location': location,

            'locations': regions_list(),
            'sub_regions': regions_list(location),

            'dialog': dialog,
            'signed_up_in_uik': signed_up_in_uik,
            'disqus_identifier': 'location/' + str(location.id),

            'counters': counters,

            'add_commission_member_form': CommissionMemberForm(),

            'verified_protocols': verified_protocols,
            'protocol_data': protocol_data,
            'cik_data': cik_data,
        })

        ctx.update(self.update_context())
        return ctx

location_view = BaseLocationView.as_view()

class InfoView(BaseLocationView):
    def update_context(self):
        return {'commission_members': CommissionMember.objects.filter(location=self.location)}

class ParticipantsView(BaseLocationView):
    def update_context(self):
        role_type = self.request.GET.get('type', '')
        if not role_type in ROLE_TYPES:
            role_type = ''

        role_queryset = Role.objects.filter(self.location_query)
        if role_type:
            role_queryset = role_queryset.filter(type=role_type)
            roles = role_queryset.order_by('user__username').select_related('user', 'organization')[:100]
            context = {'participants': roles}
        else:
            roles = role_queryset.order_by('user__username').select_related('user', 'organization')[:100]
            users = sorted(set(role.user for role in roles), key=lambda user: user.username.lower())
            context = {'users': users}

        context.update({
            'selected_role_type': role_type,
            'ROLE_CHOICES': ROLE_CHOICES,
        })
        return context

# TODO: mark links previously reported by user
class LinksView(BaseLocationView):
    def update_context(self):
        return {
            'view': 'locations/links.html',
            'links': list(Link.objects.filter(location=self.location)),
        }

class WebObserversView(BaseLocationView):
    def update_context(self):
        web_observers = WebObserver.objects.filter(location=self.location).select_related('user__user')
        web_observers_by_time = {}
        for web_observer in web_observers:
            for time in range(web_observer.start_time, web_observer.end_time):
                web_observers_by_time.setdefault(time, []).append(web_observer)

        times = []
        for time in range(7, 24):
            times.append({'start_time': time, 'web_observers': web_observers_by_time.get(time, [])})
            times[-1]['end_time'] = time+1 if time<23 else 0

        return {
            'view': 'locations/web_observers.html',
            'times': times,
            'become_web_observer_form': WebObserverForm(),
        }

class ViolationsView(BaseLocationView):
    def update_context(self):
        return {
            'view': 'locations/violations.html',
            'violations': Violation.objects.filter(self.location_query)[:100]
        }

class ProtocolsView(BaseLocationView):
    def update_context(self):
        protocols = Protocol.objects.from_users().filter(self.location_query).select_related('location')[:100]
        return {
            'view': 'locations/protocols.html',
            'protocols': protocols,
        }

class OrganizationsView(BaseLocationView):
    def update_context(self):
        organizations = OrganizationCoverage.objects.organizations_at_location(self.location)
        return {
            'view': 'locations/organizations.html',
            'organizations': organizations,
        }

def location_supporters(request, loc_id):
    return HttpResponsePermanentRedirect(reverse('location_wall', kwargs={'loc_id': loc_id}))

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

# TODO: restructure it and take only one parameter
def goto_location(request):
    tab = request.GET.get('tab', 'wall')
    dialog = request.GET.get('dialog', '')
    for name in ('uik', 'tik', 'region'):
        try:
            location_id = int(request.GET.get(name, ''))
        except ValueError:
            continue

        url = reverse('location_info', args=[location_id])
        if tab:
            url += '/' + tab
        if dialog:
            url += '?dialog=' + dialog
        return HttpResponseRedirect(url)

    return HttpResponseRedirect(reverse('main'))

def locations_data(request):
    """ level = 2, 3, 4 """
    coords = {}
    for name in ('x1', 'y1', 'x2', 'y2'):
        try:
            coords[name] = float(request.GET.get(name, ''))
        except ValueError:
            return HttpResponse('"error"')

    try:
        level = int(request.GET.get('level', ''))
    except ValueError:
        return HttpResponse('"error"')

    if level not in (2, 3, 4):
        return HttpResponse('"error"')

    queryset = Location.objects.filter(x_coord__gt=coords['x1'], x_coord__lt=coords['x2'],
            y_coord__gt=coords['y1'], y_coord__lt=coords['y2'])

    return get_locations_data(queryset, level)

def boundaries_data(request):
    coords = {}
    for name in ('x1', 'y1', 'x2', 'y2'):
        try:
            coords[name] = float(request.GET.get(name, ''))
        except ValueError:
            return HttpResponse('"error"')

    boundaries = Boundary.objects.filter(x_min__lte=coords['x2'], x_max__gte=coords['x1'],
            y_min__lte=coords['y2'], y_max__gte=coords['y1']).values_list('data', flat=True)

    return HttpResponse('['+','.join(boundaries)+']')
