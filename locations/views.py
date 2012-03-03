# coding=utf8
import json

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.views.generic.base import TemplateView

from grakon.utils import authenticated_redirect
from locations.models import Location
from locations.utils import get_locations_data, get_roles_counters, regions_list
from organizations.models import OrganizationCoverage
from links.models import Link
from users.forms import CommissionMemberForm, WebObserverForm
from users.models import CommissionMember, Role, ROLE_TYPES, WebObserver

# TODO: don't query lists of roles if it's not needed
# TODO: mark links previously reported by user
# TODO: web_observers and supporters tabs are not activated for tiks and lead to crush
class LocationView(TemplateView):
    template_name = 'locations/base.html'

    def get_context_data(self, **kwargs):
        ctx = super(LocationView, self).get_context_data(**kwargs)

        loc_id = int(kwargs['loc_id'])
        try:
            location = Location.objects.select_related().get(id=loc_id)
        except Location.DoesNotExist:
            raise Http404(u'Избирательный округ не найден')

        # Get the list of role
        query = Q(location=location)
        if not location.tik:
            query |= Q(location__tik=location) if location.region else Q(location__region=location)

        participants = Role.objects.get_participants(query)

        # Get sub-regions
        sub_regions = []

        # TODO: index by region, tik, name is needed to sort by name inside db
        if location.region is None:
            sub_regions += list(Location.objects.filter(region=location, tik=None).values_list('id', 'name')) #.order_by('name')
        elif location.tik is None:
            sub_regions += list(Location.objects.filter(tik=location).values_list('id', 'name')) # .order_by('name')

        sub_regions = sorted(sub_regions, None, lambda r: r[1])

        dialog = self.request.GET.get('dialog', '')
        if not dialog in ROLE_TYPES and not dialog in ('web_observer'):
            dialog = ''

        signed_up_in_uik = False
        if self.request.user.is_authenticated():
            voter_roles = Role.objects.filter(user=self.request.profile, type='voter').select_related('location')
            if voter_roles:
                signed_up_in_uik = voter_roles[0].location.is_uik()

        commission_members = CommissionMember.objects.filter(location=location)

        ctx.update({
            'loc_id': kwargs['loc_id'],
            'view': kwargs['view'],
            'current_location': location,
            'participants': participants,
            'links': list(Link.objects.filter(location=location)),
            'locations': regions_list(),
            'is_voter_here': self.request.user.is_authenticated() and any(self.request.user==voter.user for voter in participants.get('voter', [])),
            'sub_regions': sub_regions,
            'dialog': dialog,
            'signed_up_in_uik': signed_up_in_uik,
            'disqus_identifier': 'location/' + str(location.id),

            'counters': get_roles_counters(location),
            'organizations': OrganizationCoverage.objects.organizations_at_location(location),

            'commission_members': commission_members,
            'commission_members_count': len(commission_members),
            'add_commission_member_form': CommissionMemberForm(),
        })

        # Web observers
        web_observers = WebObserver.objects.filter(location=location).select_related('user__user')
        web_observers_by_time = {}
        for web_observer in web_observers:
            for time in range(web_observer.start_time, web_observer.end_time):
                web_observers_by_time.setdefault(time, []).append(web_observer)

        web_observers_count = len(set(web_observer.user_id for web_observer in web_observers))

        times = []
        for time in range(7, 24):
            times.append({'start_time': time, 'web_observers': web_observers_by_time.get(time, [])})
            times[-1]['end_time'] = time+1 if time<23 else 0

        ctx.update({
            'times': times,
            'web_observers_count': web_observers_count,
            'become_web_observer_form': WebObserverForm(),
        })
        return ctx

location_view = LocationView.as_view()

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
    tab = request.GET.get('tab', '')
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
