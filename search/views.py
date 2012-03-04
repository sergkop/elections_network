# -*- coding: utf-8 -*-
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic.base import TemplateView

from loginza.models import UserMap

from grakon.models import Profile
from locations.models import Location
from locations.utils import get_roles_query, regions_list
from search.utils import get_uik_data
from users.forms import RoleTypeForm
from users.models import Role, ROLE_CHOICES, ROLE_TYPES

class BaseSearchView(TemplateView):
    template_name = 'search/base.html'
    tab = '' # 'user_list', 'user_table' or 'map'

    def get_context_data(self, **kwargs):
        ctx = super(BaseSearchView, self).get_context_data(**kwargs)

        loc_id = ''
        for name in ('uik', 'tik', 'region'):
            loc_id = self.request.GET.get(name, '')
            if loc_id:
                break

        try:
            loc_id = int(loc_id)
        except ValueError:
            self.location = None
        else:
            try:
                self.location = Location.objects.get(id=loc_id)
            except Location.DoesNotExist:
                self.location = None

        role_form = RoleTypeForm(self.request.GET)

        if role_form.is_valid():
            self.role_type = role_form.cleaned_data['type']
        else:
            self.role_type = ''

        self.inactive_ids = UserMap.objects.filter(verified=False).values_list('user', flat=True)

        ctx.update({
            'tab': self.tab,
            'locations': regions_list(),
            'location_path': str(self.location.path()) if self.location else '[]',
            'role_form': role_form,
            'role_name': ROLE_TYPES[self.role_type] if self.role_type else '',
            'name': 'search', # requiered to highlight main menu item
        })
        return ctx

# TODO: show only verified users
class ListSearchView(BaseSearchView):
    tab = 'user_list'

    def get_context_data(self, **kwargs):
        ctx = super(ListSearchView, self).get_context_data(**kwargs)

        query = get_roles_query(self.location)
        if self.role_type:
            query = query & Q(type=self.role_type)

        # TODO: when role_type='' query is not correct
        profile_ids = Role.objects.filter(query).values_list('user', flat=True)
        people = Profile.objects.filter(id__in=profile_ids) \
                .exclude(user__email='', user__is_active=False, id__in=self.inactive_ids) \
                .only('username', 'show_name', 'first_name', 'last_name').order_by('username')

        result_count = len(people)

        # TODO: temporary limit until pagination is introduced
        people = people[:100]

        ctx.update({
            'people': people,
            'result_count': result_count,
        })
        return ctx

user_list = ListSearchView.as_view()

class TableSearchView(BaseSearchView):
    tab = 'user_table'

    def get_context_data(self, **kwargs):
        ctx = super(TableSearchView, self).get_context_data(**kwargs)

        if self.role_type == '':
            role_queryset = Role.objects.exclude(user__user__email='', user__user__is_active=False,
                    user__user__id__in=self.inactive_ids)

            distr = {}
            # TODO: total number for each subregion
            if not self.location:
                sub_regions = Location.objects.filter(region=None).order_by('name')

                for role_type, region in role_queryset.values_list('type', 'location__region'):
                    distr.setdefault(region, {}).setdefault(role_type, 0)
                    distr[region][role_type] += 1
            elif self.location.is_region():
                sub_regions = Location.objects.filter(region=self.location, tik=None).order_by('name')

                for role_type, tik in role_queryset.filter(location__region=self.location) \
                        .values_list('type', 'location__tik'):
                    distr.setdefault(tik, {}).setdefault(role_type, 0)
                    distr[tik][role_type] += 1
            elif self.location.is_tik():
                sub_regions = Location.objects.filter(tik=self.location).order_by('name')

                for role_type, uik in role_queryset.filter(location__tik=self.location) \
                        .values_list('type', 'location__id'):
                    distr.setdefault(uik, {}).setdefault(role_type, 0)
                    distr[uik][role_type] += 1
            elif self.location.is_uik():
                sub_regions = []

            total = {}
            for loc_id in distr:
                for role_type in distr[loc_id]:
                    total.setdefault(role_type, 0)
                    total[role_type] += distr[loc_id][role_type]

            for role_type in role_queryset.filter(location=self.location) \
                    .values_list('type', flat=True):
                total.setdefault(role_type, 0)
                total[role_type] += 1

            lines = []
            for sub_region in sub_regions:
                if sub_region.id in distr:
                    lines.append({'location': sub_region, 'data': distr.get(sub_region.id, {})})

            ctx.update({
                'lines': lines,
                'total': total,
            })
        return ctx

user_table = TableSearchView.as_view()

class MapSearchView(BaseSearchView):
    tab = 'map'

    def get_context_data(self, **kwargs):
        ctx = super(MapSearchView, self).get_context_data(**kwargs)

        ctx.update({
            'zoom': self.request.GET.get('zoom', ''),
            'lat': self.request.GET.get('lat', ''),
            'lon': self.request.GET.get('lon', '')
        })
        return ctx

map = MapSearchView.as_view()

class FindUikView(BaseSearchView):
    tab = 'find_uik'

find_uik = FindUikView.as_view()

def uik_search_data(request):
    return HttpResponse(get_uik_data(request.GET))
